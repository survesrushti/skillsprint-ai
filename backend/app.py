import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

from extensions import db


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "skillsprint-ai-local-secret"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://localhost:5174"
                ]
            }
        }
    )

    db.init_app(app)

    from models import (
        User,
        Track,
        Topic,
        TopicPrerequisite,
        Resource,
        Goal,
        StudyLog,
        Roadmap,
        RoadmapItem,
        WeeklyReflection
    )

    from routes.goals import goals_bp
    from routes.roadmap import roadmap_bp
    from routes.tasks import tasks_bp
    from routes.progress import progress_bp
    from routes.tracks import tracks_bp
    from routes.resources import resources_bp
    from routes.reflections import reflections_bp
    from middleware.auth import authenticate_request

    app.before_request(authenticate_request)

    app.register_blueprint(goals_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(tracks_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(reflections_bp)

    with app.app_context():
        try:
            db.create_all()
        except Exception as db_init_err:
            app.logger.warning(f"db.create_all() notice: {db_init_err}")

    @app.get("/api/v1/health")
    def health():
        return jsonify({
            "status": "ok",
            "message": "SkillSprint AI backend is running"
        })

    @app.get("/api/v1/db-test")
    def db_test():
        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return jsonify({
                "status": "ok",
                "message": "MySQL database connection is working"
            })

        except Exception as error:
            return jsonify({
                "status": "error",
                "message": "MySQL database connection failed",
                "error": str(error)
            }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )