from extensions import db


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(
        db.Integer,
        db.ForeignKey("tracks.id"),
        nullable=False
    )
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=1)
    priority = db.Column(db.Float, nullable=False, default=1.0)
    is_optional = db.Column(db.Boolean, default=False, nullable=False)

    prerequisites = db.relationship(
        "TopicPrerequisite",
        foreign_keys="TopicPrerequisite.topic_id",
        backref="topic",
        lazy=True,
        cascade="all, delete-orphan"
    )