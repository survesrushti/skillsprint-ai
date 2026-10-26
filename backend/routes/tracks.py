from flask import Blueprint, jsonify

from extensions import db
from models import Track, Topic, TopicPrerequisite


tracks_bp = Blueprint(
    "tracks",
    __name__,
    url_prefix="/api/v1/tracks"
)


SLUG_ALIASES = {
    "full-stack": "full-stack-development",
    "ui-ux": "ui-ux-design",
}


def _serialize_topic(topic):
    return {
        "id": topic.id,
        "name": topic.name,
        "slug": topic.slug,
        "description": topic.description,
        "estimated_minutes": topic.estimated_minutes,
        "difficulty": topic.difficulty,
        "priority": topic.priority,
        "is_optional": topic.is_optional,
        "prerequisites": [
            p.prerequisite_topic_id
            for p in topic.prerequisites
        ]
    }


def _serialize_track(track, include_topics=True):
    topics = sorted(track.topics, key=lambda t: t.id)
    total_minutes = sum(t.estimated_minutes for t in topics)

    weeks = max(4, round(total_minutes / (2 * 60 * 7)))
    duration = f"{weeks}–{weeks + 2} weeks"

    data = {
        "id": track.id,
        "name": track.name,
        "slug": track.slug,
        "description": track.description,
        "is_active": track.is_active,
        "topic_count": len(topics),
        "total_minutes": total_minutes,
        "estimated_duration": duration,
    }

    if include_topics:
        data["topics"] = [
            _serialize_topic(topic)
            for topic in topics
        ]

    return data


@tracks_bp.get("")
def get_tracks():
    try:
        tracks = Track.query.filter_by(
            is_active=True
        ).order_by(
            Track.id
        ).all()

        return jsonify({
            "status": "success",
            "count": len(tracks),
            "tracks": [
                _serialize_track(track, include_topics=True)
                for track in tracks
            ]
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Could not retrieve learning tracks.",
            "error": str(error)
        }), 500


@tracks_bp.get("/<slug_or_id>")
def get_track(slug_or_id):
    try:
        track = None

        # Check if requested by numeric ID
        if slug_or_id.isdigit():
            track = db.session.get(Track, int(slug_or_id))

        if track is None:
            # Check direct slug
            track = Track.query.filter_by(slug=slug_or_id).first()

        if track is None and slug_or_id in SLUG_ALIASES:
            # Check known alias
            canonical_slug = SLUG_ALIASES[slug_or_id]
            track = Track.query.filter_by(slug=canonical_slug).first()

        if track is None:
            return jsonify({
                "status": "error",
                "message": f"Track '{slug_or_id}' not found."
            }), 404

        return jsonify({
            "status": "success",
            "track": _serialize_track(track, include_topics=True)
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": f"Could not retrieve track '{slug_or_id}'.",
            "error": str(error)
        }), 500

