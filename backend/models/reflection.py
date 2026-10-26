from datetime import datetime
from extensions import db


class WeeklyReflection(db.Model):
    __tablename__ = "weekly_reflections"

    id = db.Column(db.Integer, primary_key=True)

    goal_id = db.Column(
        db.Integer,
        db.ForeignKey("goals.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    week_number = db.Column(
        db.Integer,
        nullable=False
    )

    study_day = db.Column(
        db.Integer,
        nullable=False
    )

    confidence_level = db.Column(
        db.Integer,
        nullable=False
    )

    difficulty_rating = db.Column(
        db.Integer,
        nullable=False
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "week_number": self.week_number,
            "study_day": self.study_day,
            "confidence_level": self.confidence_level,
            "difficulty_rating": self.difficulty_rating,
            "notes": self.notes,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

