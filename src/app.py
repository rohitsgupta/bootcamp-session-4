"""
Slalom Capabilities Management System API.

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Slalom Capabilities Management API",
    description="API for managing consulting capabilities and consultant expertise",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

DB_PATH = os.getenv("CAPABILITIES_DB_PATH", str(current_dir / "capabilities.db"))

# Seed data used when the database is empty.
DEFAULT_CAPABILITIES = {
    "Cloud Architecture": {
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,  # hours per week available across team
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
    },
    "Data Analytics": {
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology", 
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
    },
    "DevOps Engineering": {
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"], 
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
    },
    "Digital Strategy": {
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
    },
    "Change Management": {
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
    },
    "UX/UI Design": {
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
    },
    "Cybersecurity": {
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
    },
    "Business Intelligence": {
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
    },
    "Agile Coaching": {
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
    }
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate_database(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS capabilities (
            name TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            practice_area TEXT NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity >= 0)
        );

        CREATE TABLE IF NOT EXISTS consultants (
            email TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS capability_skill_levels (
            capability_name TEXT NOT NULL,
            level TEXT NOT NULL,
            level_order INTEGER NOT NULL,
            PRIMARY KEY (capability_name, level),
            FOREIGN KEY (capability_name) REFERENCES capabilities(name) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS capability_certifications (
            capability_name TEXT NOT NULL,
            certification TEXT NOT NULL,
            cert_order INTEGER NOT NULL,
            PRIMARY KEY (capability_name, certification),
            FOREIGN KEY (capability_name) REFERENCES capabilities(name) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS capability_industry_verticals (
            capability_name TEXT NOT NULL,
            industry_vertical TEXT NOT NULL,
            vertical_order INTEGER NOT NULL,
            PRIMARY KEY (capability_name, industry_vertical),
            FOREIGN KEY (capability_name) REFERENCES capabilities(name) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS capability_consultants (
            capability_name TEXT NOT NULL,
            consultant_email TEXT NOT NULL,
            PRIMARY KEY (capability_name, consultant_email),
            FOREIGN KEY (capability_name) REFERENCES capabilities(name) ON DELETE CASCADE,
            FOREIGN KEY (consultant_email) REFERENCES consultants(email) ON DELETE CASCADE
        );
        """
    )


def seed_database_if_empty(conn: sqlite3.Connection) -> None:
    count_row = conn.execute("SELECT COUNT(*) AS count FROM capabilities").fetchone()
    if count_row and count_row["count"] > 0:
        return

    for name, details in DEFAULT_CAPABILITIES.items():
        conn.execute(
            """
            INSERT INTO capabilities (name, description, practice_area, capacity)
            VALUES (?, ?, ?, ?)
            """,
            (name, details["description"], details["practice_area"], details["capacity"]),
        )

        for idx, level in enumerate(details.get("skill_levels", [])):
            conn.execute(
                """
                INSERT INTO capability_skill_levels (capability_name, level, level_order)
                VALUES (?, ?, ?)
                """,
                (name, level, idx),
            )

        for idx, cert in enumerate(details.get("certifications", [])):
            conn.execute(
                """
                INSERT INTO capability_certifications (capability_name, certification, cert_order)
                VALUES (?, ?, ?)
                """,
                (name, cert, idx),
            )

        for idx, industry in enumerate(details.get("industry_verticals", [])):
            conn.execute(
                """
                INSERT INTO capability_industry_verticals (capability_name, industry_vertical, vertical_order)
                VALUES (?, ?, ?)
                """,
                (name, industry, idx),
            )

        for consultant_email in details.get("consultants", []):
            conn.execute(
                "INSERT OR IGNORE INTO consultants (email) VALUES (?)",
                (consultant_email,),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO capability_consultants (capability_name, consultant_email)
                VALUES (?, ?)
                """,
                (name, consultant_email),
            )


def initialize_database() -> None:
    with get_connection() as conn:
        migrate_database(conn)
        seed_database_if_empty(conn)
        conn.commit()


def build_capabilities_response(
    *,
    limit: int | None = None,
    offset: int = 0,
    practice_area: str | None = None,
    search: str | None = None,
) -> dict[str, dict]:
    where_clauses: list[str] = []
    params: list = []

    if practice_area:
        where_clauses.append("practice_area = ?")
        params.append(practice_area)

    if search:
        where_clauses.append("(name LIKE ? OR description LIKE ?)")
        like_term = f"%{search}%"
        params.extend([like_term, like_term])

    where_sql = ""
    if where_clauses:
        where_sql = f"WHERE {' AND '.join(where_clauses)}"

    query = (
        "SELECT name, description, practice_area, capacity "
        f"FROM capabilities {where_sql} ORDER BY name"
    )

    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    capabilities_payload: dict[str, dict] = {}
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        for row in rows:
            cap_name = row["name"]
            skill_levels = [
                r["level"]
                for r in conn.execute(
                    """
                    SELECT level FROM capability_skill_levels
                    WHERE capability_name = ?
                    ORDER BY level_order
                    """,
                    (cap_name,),
                ).fetchall()
            ]
            certifications = [
                r["certification"]
                for r in conn.execute(
                    """
                    SELECT certification FROM capability_certifications
                    WHERE capability_name = ?
                    ORDER BY cert_order
                    """,
                    (cap_name,),
                ).fetchall()
            ]
            industry_verticals = [
                r["industry_vertical"]
                for r in conn.execute(
                    """
                    SELECT industry_vertical FROM capability_industry_verticals
                    WHERE capability_name = ?
                    ORDER BY vertical_order
                    """,
                    (cap_name,),
                ).fetchall()
            ]
            consultants = [
                r["consultant_email"]
                for r in conn.execute(
                    """
                    SELECT consultant_email FROM capability_consultants
                    WHERE capability_name = ?
                    ORDER BY consultant_email
                    """,
                    (cap_name,),
                ).fetchall()
            ]

            capabilities_payload[cap_name] = {
                "description": row["description"],
                "practice_area": row["practice_area"],
                "skill_levels": skill_levels,
                "certifications": certifications,
                "industry_verticals": industry_verticals,
                "capacity": row["capacity"],
                "consultants": consultants,
            }

    return capabilities_payload


def ensure_capability_exists(capability_name: str) -> None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM capabilities WHERE name = ?", (capability_name,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Capability not found")


@app.on_event("startup")
def startup_event() -> None:
    initialize_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
@app.get("/v1/capabilities")
def get_capabilities(
    limit: int | None = Query(default=None, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    practice_area: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    return build_capabilities_response(
        limit=limit,
        offset=offset,
        practice_area=practice_area,
        search=search,
    )


@app.post("/capabilities/{capability_name}/register")
@app.post("/v1/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str):
    """Register a consultant for a capability"""
    ensure_capability_exists(capability_name)

    with get_connection() as conn:
        already_registered = conn.execute(
            """
            SELECT 1 FROM capability_consultants
            WHERE capability_name = ? AND consultant_email = ?
            """,
            (capability_name, email),
        ).fetchone()
        if already_registered:
            raise HTTPException(
                status_code=400,
                detail="Consultant is already registered for this capability",
            )

        conn.execute("INSERT OR IGNORE INTO consultants (email) VALUES (?)", (email,))
        conn.execute(
            """
            INSERT INTO capability_consultants (capability_name, consultant_email)
            VALUES (?, ?)
            """,
            (capability_name, email),
        )
        conn.commit()

    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
@app.delete("/v1/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str):
    """Unregister a consultant from a capability"""
    ensure_capability_exists(capability_name)

    with get_connection() as conn:
        registered = conn.execute(
            """
            SELECT 1 FROM capability_consultants
            WHERE capability_name = ? AND consultant_email = ?
            """,
            (capability_name, email),
        ).fetchone()
        if not registered:
            raise HTTPException(
                status_code=400,
                detail="Consultant is not registered for this capability",
            )

        conn.execute(
            """
            DELETE FROM capability_consultants
            WHERE capability_name = ? AND consultant_email = ?
            """,
            (capability_name, email),
        )
        conn.commit()

    return {"message": f"Unregistered {email} from {capability_name}"}
