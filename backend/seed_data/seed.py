import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extensions import db
from models import Track, Topic, TopicPrerequisite, Resource


TRACKS = [
    {
        "name": "Full Stack Development",
        "slug": "full-stack-development",
        "description": "Learn frontend, backend, databases, APIs, and deployment.",
    },
    {
        "name": "Data Analytics",
        "slug": "data-analytics",
        "description": "Learn Python, data analysis, visualization, statistics, and dashboards.",
    },
    {
        "name": "UI/UX Design",
        "slug": "ui-ux-design",
        "description": "Learn user research, wireframing, visual design, prototyping, and usability.",
    },
]


TOPICS = {
    "full-stack-development": [
        {
            "name": "HTML Fundamentals",
            "slug": "html-fundamentals",
            "description": "Learn the structure and semantic elements of web pages.",
            "estimated_minutes": 180,
            "difficulty": 1,
            "priority": 1.0,
            "is_optional": False,
        },
        {
            "name": "CSS Fundamentals",
            "slug": "css-fundamentals",
            "description": "Learn styling, layouts, responsive design, and modern CSS.",
            "estimated_minutes": 240,
            "difficulty": 1,
            "priority": 1.0,
            "is_optional": False,
        },
        {
            "name": "JavaScript Fundamentals",
            "slug": "javascript-fundamentals",
            "description": "Learn variables, functions, arrays, objects, DOM, and modern JavaScript.",
            "estimated_minutes": 360,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Git and GitHub",
            "slug": "git-and-github",
            "description": "Learn version control and collaborative development workflows.",
            "estimated_minutes": 180,
            "difficulty": 1,
            "priority": 0.9,
            "is_optional": True,
        },
        {
            "name": "React Fundamentals",
            "slug": "react-fundamentals",
            "description": "Learn components, props, state, hooks, and React application structure.",
            "estimated_minutes": 360,
            "difficulty": 3,
            "priority": 1.3,
            "is_optional": False,
        },
        {
            "name": "Backend with Flask",
            "slug": "backend-with-flask",
            "description": "Learn REST APIs, routing, request handling, and backend development with Flask.",
            "estimated_minutes": 360,
            "difficulty": 3,
            "priority": 1.3,
            "is_optional": False,
        },
        {
            "name": "SQL and Databases",
            "slug": "sql-and-databases",
            "description": "Learn relational databases, SQL queries, tables, joins, and relationships.",
            "estimated_minutes": 300,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "REST API Integration",
            "slug": "rest-api-integration",
            "description": "Learn how frontend and backend applications communicate through APIs.",
            "estimated_minutes": 240,
            "difficulty": 3,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Full Stack Project",
            "slug": "full-stack-project",
            "description": "Build and integrate a complete full-stack application.",
            "estimated_minutes": 480,
            "difficulty": 4,
            "priority": 1.5,
            "is_optional": False,
        },
    ],
    "data-analytics": [
        {
            "name": "Python Fundamentals",
            "slug": "python-fundamentals",
            "description": "Learn Python syntax, data types, functions, collections, and file handling.",
            "estimated_minutes": 360,
            "difficulty": 1,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "NumPy Fundamentals",
            "slug": "numpy-fundamentals",
            "description": "Learn numerical computing and array operations using NumPy.",
            "estimated_minutes": 180,
            "difficulty": 2,
            "priority": 1.0,
            "is_optional": False,
        },
        {
            "name": "Pandas Fundamentals",
            "slug": "pandas-fundamentals",
            "description": "Learn data loading, cleaning, filtering, grouping, and transformation with Pandas.",
            "estimated_minutes": 300,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Data Cleaning",
            "slug": "data-cleaning",
            "description": "Learn how to handle missing values, duplicates, outliers, and inconsistent data.",
            "estimated_minutes": 240,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Statistics for Data Analysis",
            "slug": "statistics-for-data-analysis",
            "description": "Learn descriptive statistics, distributions, correlation, and basic statistical reasoning.",
            "estimated_minutes": 360,
            "difficulty": 3,
            "priority": 1.3,
            "is_optional": False,
        },
        {
            "name": "Data Visualization",
            "slug": "data-visualization",
            "description": "Learn charts, visual storytelling, and interactive visualization techniques.",
            "estimated_minutes": 300,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Exploratory Data Analysis",
            "slug": "exploratory-data-analysis",
            "description": "Learn how to investigate datasets and discover patterns and relationships.",
            "estimated_minutes": 300,
            "difficulty": 3,
            "priority": 1.3,
            "is_optional": False,
        },
        {
            "name": "Dashboard Development",
            "slug": "dashboard-development",
            "description": "Learn how to communicate analytical findings through dashboards.",
            "estimated_minutes": 300,
            "difficulty": 3,
            "priority": 1.1,
            "is_optional": True,
        },
        {
            "name": "Data Analytics Project",
            "slug": "data-analytics-project",
            "description": "Complete an end-to-end data analytics project.",
            "estimated_minutes": 480,
            "difficulty": 4,
            "priority": 1.5,
            "is_optional": False,
        },
    ],
    "ui-ux-design": [
        {
            "name": "Introduction to UI/UX",
            "slug": "introduction-to-ui-ux",
            "description": "Understand user interface design and user experience principles.",
            "estimated_minutes": 180,
            "difficulty": 1,
            "priority": 1.0,
            "is_optional": False,
        },
        {
            "name": "User Research",
            "slug": "user-research",
            "description": "Learn user interviews, surveys, personas, and research methods.",
            "estimated_minutes": 240,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Information Architecture",
            "slug": "information-architecture",
            "description": "Learn how to organize information and create effective navigation structures.",
            "estimated_minutes": 240,
            "difficulty": 2,
            "priority": 1.1,
            "is_optional": False,
        },
        {
            "name": "Wireframing",
            "slug": "wireframing",
            "description": "Create low-fidelity layouts to plan digital interfaces.",
            "estimated_minutes": 240,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Visual Design",
            "slug": "visual-design",
            "description": "Learn color, typography, spacing, hierarchy, and visual composition.",
            "estimated_minutes": 300,
            "difficulty": 2,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "Figma Fundamentals",
            "slug": "figma-fundamentals",
            "description": "Learn the basic tools and workflows for designing interfaces in Figma.",
            "estimated_minutes": 240,
            "difficulty": 1,
            "priority": 1.0,
            "is_optional": True,
        },
        {
            "name": "Prototyping",
            "slug": "prototyping",
            "description": "Learn interactive prototypes and user flow simulation.",
            "estimated_minutes": 300,
            "difficulty": 3,
            "priority": 1.3,
            "is_optional": False,
        },
        {
            "name": "Usability Testing",
            "slug": "usability-testing",
            "description": "Learn how to evaluate designs through usability testing.",
            "estimated_minutes": 240,
            "difficulty": 3,
            "priority": 1.2,
            "is_optional": False,
        },
        {
            "name": "UI/UX Design Project",
            "slug": "ui-ux-design-project",
            "description": "Complete an end-to-end UI/UX design project.",
            "estimated_minutes": 480,
            "difficulty": 4,
            "priority": 1.5,
            "is_optional": False,
        },
    ],
}


PREREQUISITES = {
    "full-stack-development": [
        ("css-fundamentals", "html-fundamentals"),
        ("javascript-fundamentals", "html-fundamentals"),
        ("javascript-fundamentals", "css-fundamentals"),
        ("react-fundamentals", "javascript-fundamentals"),
        ("git-and-github", "html-fundamentals"),
        ("backend-with-flask", "python-fundamentals"),
        ("rest-api-integration", "react-fundamentals"),
        ("rest-api-integration", "backend-with-flask"),
        ("full-stack-project", "react-fundamentals"),
        ("full-stack-project", "backend-with-flask"),
        ("full-stack-project", "sql-and-databases"),
        ("full-stack-project", "rest-api-integration"),
    ],
    "data-analytics": [
        ("numpy-fundamentals", "python-fundamentals"),
        ("pandas-fundamentals", "python-fundamentals"),
        ("data-cleaning", "pandas-fundamentals"),
        ("statistics-for-data-analysis", "python-fundamentals"),
        ("data-visualization", "pandas-fundamentals"),
        ("exploratory-data-analysis", "pandas-fundamentals"),
        ("exploratory-data-analysis", "data-cleaning"),
        ("exploratory-data-analysis", "statistics-for-data-analysis"),
        ("dashboard-development", "data-visualization"),
        ("data-analytics-project", "exploratory-data-analysis"),
        ("data-analytics-project", "data-visualization"),
    ],
    "ui-ux-design": [
        ("user-research", "introduction-to-ui-ux"),
        ("information-architecture", "user-research"),
        ("wireframing", "information-architecture"),
        ("visual-design", "introduction-to-ui-ux"),
        ("figma-fundamentals", "visual-design"),
        ("prototyping", "wireframing"),
        ("prototyping", "visual-design"),
        ("usability-testing", "prototyping"),
        ("ui-ux-design-project", "usability-testing"),
        ("ui-ux-design-project", "visual-design"),
    ],
}


RESOURCES = {
    "html-fundamentals": [
        ("MDN HTML Guide", "https://developer.mozilla.org/en-US/docs/Web/HTML", "documentation"),
    ],
    "css-fundamentals": [
        ("MDN CSS Guide", "https://developer.mozilla.org/en-US/docs/Web/CSS", "documentation"),
    ],
    "javascript-fundamentals": [
        ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "documentation"),
    ],
    "git-and-github": [
        ("GitHub Git Handbook", "https://docs.github.com/en/get-started/learning-to-code/getting-started-with-git", "documentation"),
    ],
    "react-fundamentals": [
        ("React Documentation", "https://react.dev/learn", "documentation"),
    ],
    "backend-with-flask": [
        ("Flask Documentation", "https://flask.palletsprojects.com/", "documentation"),
    ],
    "sql-and-databases": [
        ("MySQL Documentation", "https://dev.mysql.com/doc/", "documentation"),
    ],
    "python-fundamentals": [
        ("Python Documentation", "https://docs.python.org/3/tutorial/", "documentation"),
    ],
    "numpy-fundamentals": [
        ("NumPy Documentation", "https://numpy.org/doc/stable/", "documentation"),
    ],
    "pandas-fundamentals": [
        ("Pandas Documentation", "https://pandas.pydata.org/docs/", "documentation"),
    ],
    "data-visualization": [
        ("Plotly Python Documentation", "https://plotly.com/python/", "documentation"),
    ],
    "statistics-for-data-analysis": [
        ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "course"),
    ],
    "introduction-to-ui-ux": [
        ("Nielsen Norman Group", "https://www.nngroup.com/articles/", "articles"),
    ],
    "user-research": [
        ("Nielsen Norman Group - User Research", "https://www.nngroup.com/topic/user-research/", "articles"),
    ],
    "information-architecture": [
        ("Nielsen Norman Group - Information Architecture", "https://www.nngroup.com/topic/information-architecture/", "articles"),
    ],
    "wireframing": [
        ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613", "documentation"),
    ],
    "visual-design": [
        ("Material Design", "https://m3.material.io/", "design system"),
    ],
    "figma-fundamentals": [
        ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613", "documentation"),
    ],
    "prototyping": [
        ("Figma Prototyping Guide", "https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma", "documentation"),
    ],
    "usability-testing": [
        ("Nielsen Norman Group - Usability Testing", "https://www.nngroup.com/articles/usability-testing-101/", "articles"),
    ],
}


def seed_database():
    with app.app_context():
        print("Clearing existing catalog data...")

        TopicPrerequisite.query.delete()
        Resource.query.delete()
        Topic.query.delete()
        Track.query.delete()

        db.session.commit()

        track_objects = {}

        print("Creating tracks...")

        for track_data in TRACKS:
            track = Track(**track_data)
            db.session.add(track)
            track_objects[track.slug] = track

        db.session.flush()

        topic_objects = {}

        print("Creating topics...")

        for track_slug, topics in TOPICS.items():
            track = track_objects[track_slug]

            for topic_data in topics:
                topic = Topic(
                    track_id=track.id,
                    **topic_data
                )

                db.session.add(topic)
                topic_objects[topic.slug] = topic

        db.session.flush()

        print("Creating prerequisites...")

        for track_slug, prerequisites in PREREQUISITES.items():
            for topic_slug, prerequisite_slug in prerequisites:
                db.session.add(
                    TopicPrerequisite(
                        topic_id=topic_objects[topic_slug].id,
                        prerequisite_topic_id=topic_objects[prerequisite_slug].id
                    )
                )

        print("Creating resources...")

        for topic_slug, resources in RESOURCES.items():
            topic = topic_objects[topic_slug]

            for title, url, resource_type in resources:
                db.session.add(
                    Resource(
                        topic_id=topic.id,
                        title=title,
                        url=url,
                        resource_type=resource_type
                    )
                )

        db.session.commit()

        print()
        print("===================================")
        print("SkillSprint AI seed completed!")
        print("===================================")
        print(f"Tracks: {Track.query.count()}")
        print(f"Topics: {Topic.query.count()}")
        print(f"Prerequisites: {TopicPrerequisite.query.count()}")
        print(f"Resources: {Resource.query.count()}")


if __name__ == "__main__":
    seed_database()