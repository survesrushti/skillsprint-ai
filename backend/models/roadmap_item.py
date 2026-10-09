from datetime import datetime
from extensions import db


class RoadmapItem(db.Model):
    __tablename__ = "roadmap_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    roadmap_id = db.Column(
        db.Integer,
        db.ForeignKey("roadmaps.id"),
        nullable=False
    )

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.id"),
        nullable=False
    )

    day_number = db.Column(
        db.Integer,
        nullable=False
    )

    planned_minutes = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )