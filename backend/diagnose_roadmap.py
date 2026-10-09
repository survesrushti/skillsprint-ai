"""
SkillSprint AI - roadmap persistence diagnostic.
Run from the backend folder with the venv active:

    python diagnose_roadmap.py              # full diagnosis
    python diagnose_roadmap.py --no-call    # skip step 9 (the endpoint call)
    python diagnose_roadmap.py --goal 9     # choose another goal id

Step 9 calls POST /roadmap/generate in-process. If your route persists,
that creates one REAL roadmap for the goal, which is what we want to confirm.
If the script hangs at step 3, app.py starts the server on import
(missing `if __name__ == "__main__":` guard) - press Ctrl+C and tell me.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

SELF = Path(__file__).name
SKIP_DIRS = {"venv", ".venv", "env", "__pycache__", "node_modules", ".git", "site-packages"}
ROUTE_RE = re.compile(r"""\.route\(\s*['"]([^'"]*)['"]""")


def banner(title):
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


def ok(msg):
    print(f"[ OK ] {msg}")


def warn(msg):
    print(f"[WARN] {msg}")


def bad(msg):
    print(f"[FAIL] {msg}")


def info(msg):
    print(f"       {msg}")


def guarded(fn, *args):
    try:
        return fn(*args)
    except Exception:
        bad(f"{fn.__name__} crashed:")
        traceback.print_exc()
        return None


def iter_py_files():
    for root, dirs, files in os.walk(BACKEND):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".py") and name != SELF:
                yield Path(root) / name


# ---------------------------------------------------------------- 1
def check_environment():
    banner("1. ENVIRONMENT")
    info(f"Working dir : {Path.cwd()}")
    info(f"Backend dir : {BACKEND}")
    info(f"Python      : {sys.executable}")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    (ok if in_venv else warn)(f"Virtual environment active: {in_venv}")
    if Path.cwd().resolve() != BACKEND:
        warn("Not running from backend/ - imports like 'from extensions import db' may differ from the server's.")


# ---------------------------------------------------------------- 2
def scan_sources():
    banner("2. SOURCE SCAN (every .py file under backend/)")
    roadmap_named, route_hits, register_hits, model_use = [], [], [], []
    for path in iter_py_files():
        rel = path.relative_to(BACKEND)
        if path.stem.lower().startswith("roadmap"):
            roadmap_named.append(rel)
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            m = ROUTE_RE.search(line)
            if m and re.search(r"roadmap|generate", m.group(1), re.I):
                route_hits.append((rel, n, line.strip()))
            if "register_blueprint" in line:
                register_hits.append((rel, n, line.strip()))
            if re.search(r"\b(Roadmap|RoadmapItem)\(", line):
                model_use.append((rel, n, line.strip()))

    def show(title, hits):
        print(f"\n  {title}")
        if not hits:
            info("(none)")
        for rel, n, line in hits:
            info(f"{rel}:{n}  {line}")

    print("\n  Files whose name starts with 'roadmap' (look for copies/backups):")
    for rel in roadmap_named or ["(none)"]:
        info(str(rel))
    if len(roadmap_named) > 1:
        warn("More than one roadmap-like file. Make sure you edited the one that is registered.")

    show("Route decorators mentioning 'roadmap' or 'generate':", route_hits)
    if len({h[0] for h in route_hits if "generate" in h[2]}) > 1:
        bad("'generate' route is defined in more than one file.")
    show("register_blueprint calls:", register_hits)
    show("Places that construct Roadmap(...) / RoadmapItem(...):", model_use)
    if not model_use:
        bad("No file under backend/ constructs Roadmap(...) - persistence code is NOT saved anywhere.")


# ---------------------------------------------------------------- 3
def load_app():
    banner("3. LOADING THE FLASK APP")
    from flask import Flask

    try:
        mod = importlib.import_module("app")
    except Exception:
        bad("Could not import app.py (import/path problem):")
        traceback.print_exc()
        return None
    info(f"Module 'app' loaded from: {getattr(mod, '__file__', '?')}")
    flask_app = getattr(mod, "app", None)
    if not isinstance(flask_app, Flask):
        factory = getattr(mod, "create_app", None)
        flask_app = factory() if callable(factory) else None
    if flask_app is None:
        bad("Found neither an 'app' Flask object nor a create_app() factory in app.py.")
        return None
    ok("Flask app object ready")
    return flask_app


# ---------------------------------------------------------------- 4
def inspect_routes(flask_app):
    banner("4. REGISTERED ROUTES / BLUEPRINTS")
    info("Blueprints: " + (", ".join(f"{n} (prefix={bp.url_prefix})" for n, bp in flask_app.blueprints.items()) or "(none)"))
    print()
    generate_rules = []
    for rule in sorted(flask_app.url_map.iter_rules(), key=lambda r: r.rule):
        if "roadmap" not in rule.rule.lower():
            continue
        view = flask_app.view_functions.get(rule.endpoint)
        func = inspect.unwrap(view) if view else None
        where = "?"
        if func is not None and hasattr(func, "__code__"):
            where = f"{func.__code__.co_filename}:{func.__code__.co_firstlineno}"
        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
        info(f"{methods} {rule.rule} -> {rule.endpoint}")
        info(f"      defined at {where}")
        if rule.rule.endswith("/roadmap/generate") and "POST" in rule.methods:
            generate_rules.append((rule, view))

    print()
    if not generate_rules:
        bad("No POST .../roadmap/generate route is registered - blueprint not registered, or different URL.")
        return None, None
    if len(generate_rules) > 1:
        bad("More than one POST .../roadmap/generate is registered:")
        for rule, _ in generate_rules:
            info(f"{rule.rule} -> {rule.endpoint}")
    rule, view = generate_rules[0]
    ok(f"POST {rule.rule} is served by endpoint '{rule.endpoint}'")
    return rule.rule, view


# ---------------------------------------------------------------- 5
def inspect_handler(view):
    banner("5. HANDLER SOURCE (the code Flask will actually run)")
    func = inspect.unwrap(view)
    src_file = inspect.getsourcefile(func)
    lines, start = inspect.getsourcelines(func)
    mtime = datetime.fromtimestamp(Path(src_file).stat().st_mtime)
    info(f"Function    : {func.__module__}.{func.__name__}")
    info(f"File        : {src_file}")
    info(f"Last saved  : {mtime:%Y-%m-%d %H:%M:%S}   (now {datetime.now():%Y-%m-%d %H:%M:%S})")

    markers = {
        "constructs Roadmap(": r"\bRoadmap\(",
        "constructs RoadmapItem(": r"\bRoadmapItem\(",
        "session.add / add_all": r"session\.(add|add_all|bulk_save_objects)\(",
        "session.commit": r"session\.commit\(",
        "session.rollback": r"session\.rollback\(",
        "mentions roadmap_id": r"roadmap_id",
        "except clause": r"^\s*except\b",
        "mentions Rescheduler": r"[Rr]eschedul",
        "return statement": r"^\s*return\b",
    }
    print()
    found = {}
    for label, pattern in markers.items():
        hits = [start + i for i, line in enumerate(lines) if re.search(pattern, line)]
        found[label] = hits
        info(f"{label:<26}: " + (", ".join(f"line {h}" for h in hits) if hits else "NOT PRESENT"))

    module = sys.modules.get(func.__module__)
    print()
    for name in ("Roadmap", "RoadmapItem", "db"):
        (ok if hasattr(module, name) else warn)(f"'{name}' is {'imported' if hasattr(module, name) else 'NOT imported'} in {func.__module__}")

    if not found["constructs Roadmap("]:
        bad("The handler on disk does NOT create a Roadmap. Either the edit was not saved here, or this is not the handler you edited.")
    if found["except clause"]:
        warn("Handler has except clause(s). Check none of them swallows an error and still returns success.")
    return {"file": src_file, "found": found}


# ---------------------------------------------------------------- 6
def inspect_rescheduler():
    banner("6. RESCHEDULER API (what the route can actually call)")
    hits = []
    for path in iter_py_files():
        try:
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                m = re.match(r"\s*class\s+(\w*Reschedul\w*)", line)
                if m:
                    hits.append((path, n, m.group(1)))
        except OSError:
            continue
    if not hits:
        warn("No class with 'Reschedul' in its name found.")
        return
    for path, n, cls_name in hits:
        rel = path.relative_to(BACKEND)
        info(f"class {cls_name}  ({rel}:{n})")
        module_name = ".".join(rel.with_suffix("").parts)
        try:
            cls = getattr(importlib.import_module(module_name), cls_name)
        except Exception as exc:
            warn(f"could not import {module_name}: {exc}")
            continue
        for name, member in inspect.getmembers(cls, lambda m: inspect.isfunction(m) or inspect.ismethod(m)):
            if not name.startswith("_") or name == "__init__":
                info(f"    {cls_name}.{name}{inspect.signature(member)}")
    info("Compare these signatures with the calls shown by step 5 / your route.")


# ---------------------------------------------------------------- 7
def check_database(flask_app, goal_id):
    banner("7. DATABASE vs MODELS")
    from sqlalchemy import inspect as sa_inspect, text
    from extensions import db
    import models

    with flask_app.app_context():
        info(f"Flask connects to : {db.engine.url.render_as_string(hide_password=True)}")
        info(f"SELECT DATABASE() : {db.session.execute(text('SELECT DATABASE()')).scalar()}")
        info("-> Make sure this is the SAME database you query in MySQL Workbench / CLI.")
        insp = sa_inspect(db.engine)

        for model in (models.Roadmap, models.RoadmapItem):
            table = model.__table__
            print(f"\n  Table '{table.name}'")
            if not insp.has_table(table.name):
                bad("table does not exist in this database")
                continue
            db_cols = {c["name"]: c for c in insp.get_columns(table.name)}
            model_cols = {c.name for c in table.columns}
            missing = model_cols - set(db_cols)
            extra = set(db_cols) - model_cols
            if missing:
                bad(f"model columns missing in DB (inserts/selects will fail): {sorted(missing)}")
            for name in sorted(extra):
                col = db_cols[name]
                required = (not col["nullable"]) and col.get("default") is None and not col.get("autoincrement")
                (bad if required else info)(
                    f"DB column '{name}' not in model" + ("  <- NOT NULL, no default: every INSERT will fail" if required else " (nullable/default, harmless)")
                )
            if not missing and not any((not db_cols[n]["nullable"]) and db_cols[n].get("default") is None and not db_cols[n].get("autoincrement") for n in extra):
                ok("model and table columns are compatible")

        counts = {t: db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in ("roadmaps", "roadmap_items")}
        print()
        info(f"Row counts now: {counts}")
        try:
            goal = db.session.get(models.Goal, goal_id)
        except Exception:
            goal = None
        (ok if goal else bad)(f"goal id {goal_id} {'exists' if goal else 'NOT FOUND'} in this database")


# ---------------------------------------------------------------- 8
def probe_insert(flask_app, goal_id):
    banner("8. ORM INSERT PROBE (rolled back, leaves no rows)")
    from extensions import db
    import models

    with flask_app.app_context():
        try:
            if not db.session.get(models.Goal, goal_id):
                bad("goal not found - skipping probe")
                return
            roadmap = models.Roadmap(goal_id=goal_id)
            db.session.add(roadmap)
            db.session.flush()
            ok(f"Roadmap row can be inserted (temporary id {roadmap.id})")
            topic = db.session.query(models.Topic).first()
            if topic is None:
                warn("no topics in DB, skipping RoadmapItem probe")
            else:
                item = models.RoadmapItem(roadmap_id=roadmap.id, topic_id=topic.id, day_number=1, planned_minutes=60)
                db.session.add(item)
                db.session.flush()
                ok(f"RoadmapItem row can be inserted (temporary id {item.id})")
        except Exception:
            bad("ORM insert failed - this is a model/schema problem:")
            traceback.print_exc()
        finally:
            db.session.rollback()


# ---------------------------------------------------------------- 9
def call_endpoint(flask_app, rule_path, goal_id):
    banner("9. IN-PROCESS CALL (tests the code currently on disk)")
    from extensions import db
    from sqlalchemy import text

    def counts():
        with flask_app.app_context():
            return {t: db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in ("roadmaps", "roadmap_items")}

    before = counts()
    flask_app.config["TESTING"] = True  # let exceptions surface here
    client = flask_app.test_client()
    result = {"before": before, "raised": False}
    try:
        resp = client.post(rule_path, json={"goal_id": goal_id})
    except Exception:
        bad("The endpoint raised an exception:")
        traceback.print_exc()
        result["raised"] = True
        return result

    data = resp.get_json(silent=True) or {}
    after = counts()
    result.update(status=resp.status_code, keys=sorted(data), after=after,
                  has_id="roadmap_id" in data, has_version=any("version" in k for k in data))
    info(f"HTTP status        : {resp.status_code}")
    info(f"Top-level keys     : {result['keys']}")
    info(f"Row counts before  : {before}")
    info(f"Row counts after   : {after}")
    days = data.get("roadmap")
    if isinstance(days, list) and days and days[0].get("tasks"):
        first = days[0]["tasks"][0]
        info(f"Shape of one task  : {sorted(first) if isinstance(first, dict) else type(first).__name__}")
    return result


# ---------------------------------------------------------------- verdict
def verdict(result, skipped):
    banner("VERDICT")
    if skipped or result is None:
        info("Step 9 was skipped. Re-run without --no-call for a definitive answer.")
        return
    if result.get("raised"):
        bad("The code on disk raises when called. Send me the traceback above.")
        return
    persisted = result["after"]["roadmaps"] > result["before"]["roadmaps"]
    if result.get("has_id") and persisted:
        ok("The code ON DISK persists correctly (response has roadmap_id and rows were written).")
        bad("So the server you call with Invoke-RestMethod is NOT running this code: stale/duplicate process or different Python.")
        info("Do Step A (kill every listener on port 5000, clear __pycache__), restart, and call again.")
    elif result.get("has_id") and not persisted:
        bad("Response claims a roadmap_id but no row exists: uncommitted session, rollback, or a different database (see step 7).")
    else:
        bad("The code ON DISK does not persist, even in-process. The edit is missing, in a different file, or in a branch that is never reached.")
        info("Send me: this output + backend/routes/roadmap.py + backend/app.py (the part that registers blueprints).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", type=int, default=9)
    parser.add_argument("--no-call", action="store_true")
    args = parser.parse_args()

    check_environment()
    guarded(scan_sources)
    flask_app = guarded(load_app)
    if flask_app is None:
        return
    rule_path, view = (guarded(inspect_routes, flask_app) or (None, None))
    if view is not None:
        guarded(inspect_handler, view)
    guarded(inspect_rescheduler)
    guarded(check_database, flask_app, args.goal)
    guarded(probe_insert, flask_app, args.goal)
    result = None
    if not args.no_call and rule_path:
        result = guarded(call_endpoint, flask_app, rule_path, args.goal)
    verdict(result, args.no_call)


if __name__ == "__main__":
    main()