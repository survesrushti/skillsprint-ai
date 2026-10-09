from extensions import db


class TopicPrerequisite(db.Model):
    __tablename__ = "topic_prerequisites"

    id = db.Column(db.Integer, primary_key=True)

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.id"),
        nullable=False
    )

    prerequisite_topic_id = db.Column(
        db.Integer,
        db.ForeignKey("topics.id"),
        nullable=False
    )