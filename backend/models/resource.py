from extensions import db


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.id"),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    resource_type = db.Column(db.String(100), nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)

    topic = db.relationship(
        "Topic",
        backref=db.backref(
            "resources",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )