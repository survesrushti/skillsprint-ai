from extensions import db


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        nullable=True
    )

    track_id = db.Column(
        db.Integer,
        db.ForeignKey("tracks.id"),
        nullable=False
    )

    skill_level = db.Column(
        db.String(50),
        nullable=False
    )

    study_hours_per_day = db.Column(
        db.Float,
        nullable=False
    )

    target_date = db.Column(
        db.Date,
        nullable=False
    )

    known_topics = db.Column(
        db.Text,
        nullable=True
    )

    commitment = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="active",
        nullable=False
    )