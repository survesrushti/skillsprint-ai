"""
collect_project_info.py - READ-ONLY helper for SkillSprint AI.
Run from the backend folder:   python collect_project_info.py
Creates inspect_bundle.txt (passwords/secrets are masked; .env is never read).
Uses only the Python standard library.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "backend" else HERE
OUT = HERE / "inspect_bundle.txt"

SKIP_DIRS = {"venv", ".venv", "env", "node_modules", "__pycache__", ".git",
             "dist", "build", ".idea", ".vscode", ".pytest_cache", "migrations"}
SKIP_FILES = {"collect_project_info.py", "diagnose_roadmap.py", ".env"}
CONTENT_DIRS = {"routes", "models", "services"}
MAX_LINES = 500

URI = re.compile(r"((?:mysql|postgres)[\w+]*://[^:/\s'\"]+:)[^@\s'\"]+(@)", re.I)
SECRET = re.compile(
    r"^(\s*['\"]?[\w.\-]*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY|PRIVATE_KEY)[\w.\-]*['\"]?\s*[=:]\s*)(.+)$",
    re.I | re.M,
)


def mask_line(match):
    value = match.group(2)
    if "getenv" in value or "environ" in value:
        return match.group(0)  # reads from environment: safe to show
    return match.group(1) + "***"


def redact(text):
    return SECRET.sub(mask_line, URI.sub(r"\1***\2", text))


def walk(folder):
    for path in sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if path.name in SKIP_DIRS:
            continue
        yield path
        if path.is_dir():
            yield from walk(path)


def wanted(path):
    if not path.is_file() or path.name in SKIP_FILES:
        return False
    rel = path.relative_to(ROOT).parts
    name = path.name.lower()
    if path.suffix == ".py":
        if "reschedul" in name:
            return True
        if rel[0] == "backend":
            if len(rel) == 2:
                return True
            if rel[1] in CONTENT_DIRS:
                return True
    if rel == ("backend", "requirements.txt") or name == ".env.example":
        return True
    if rel[0] == "frontend" and path.suffix in {".ts", ".tsx"} and "src" in rel:
        if path.parent.name in {"api", "services"} and "roadmap" in name:
            return True
        try:
            return "roadmap/generate" in path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
    return False


def main():
    lines = [f"PROJECT ROOT: {ROOT}", "", "=" * 70, "FOLDER STRUCTURE", "=" * 70]
    for path in walk(ROOT):
        depth = len(path.relative_to(ROOT).parts) - 1
        lines.append("  " * depth + path.name + ("/" if path.is_dir() else ""))

    included = [p for p in walk(ROOT) if wanted(p)]
    for path in included:
        rel = path.relative_to(ROOT)
        text = redact(path.read_text(encoding="utf-8", errors="replace"))
        body = text.splitlines()
        lines += ["", "=" * 70, f"FILE: {rel}", "=" * 70]
        lines += body[:MAX_LINES]
        if len(body) > MAX_LINES:
            lines.append(f"... [truncated, {len(body) - MAX_LINES} more lines]")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Done. Included {len(included)} files.")
    print(f"Created: {OUT}")
    print("Open it once and check no private information is visible, then send it to me.")


if __name__ == "__main__":
    main()