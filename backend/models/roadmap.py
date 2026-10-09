from datetime import datetime
from extensions import db


class Roadmap(db.Model):
    __tablename__ = "roadmaps"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    goal_id = db.Column(
        db.Integer,
        db.ForeignKey("goals.id"),
        nullable=False
    )

    version_number = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="active",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )