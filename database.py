import sqlite3
import os
import json
import hashlib
import secrets
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cliffIT.db")
DB_PATH = os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)

def get_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"

def check_password(password, hashed):
    if "$" not in hashed:
        return False
    salt, h = hashed.split("$", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == h

# ─── Default site settings ───
DEFAULT_SETTINGS = {
    "company_name": "cliffIT Solutions",
    "tagline": "Technology & Talent Solutions That Scale",
    "email": "contact@cliffitsolutions.com",
    "notification_email": "hr@cliffitsolutions.com",
    "phone": "1-800-555-1234",
    "address": "Austin, TX",
    "additional_address": "",
    "business_hours": "Mon-Fri, 8:00 AM - 6:00 PM CST",
    "linkedin_url": "#",
    "twitter_url": "#",
    "facebook_url": "#",
    "active_consultants": "1,200+",
    "client_satisfaction": "98%",
    "industries_served": "50+",
    "years_in_business": "15yr",
    "hero_badge": "Now Hiring — 500+ Open Positions",
    "hero_heading": "Technology & Talent Solutions <span>That Scale</span>",
    "hero_subtext": "From IT staffing to full-stack digital transformation, cliffIT Solutions connects businesses with the expertise they need to thrive in an evolving technology landscape.",
}

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL DEFAULT 'Full-Time',
            category TEXT NOT NULL DEFAULT 'Engineering',
            experience_level TEXT DEFAULT 'Mid-Level',
            salary_range TEXT,
            description TEXT NOT NULL,
            requirements TEXT,
            benefits TEXT,
            openings INTEGER DEFAULT 1,
            end_date TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add openings column if missing (existing DBs)
    try:
        c.execute("SELECT openings FROM jobs LIMIT 1")
    except Exception:
        c.execute("ALTER TABLE jobs ADD COLUMN openings INTEGER DEFAULT 1")

    # Add end_date column if missing (existing DBs)
    try:
        c.execute("SELECT end_date FROM jobs LIMIT 1")
    except Exception:
        c.execute("ALTER TABLE jobs ADD COLUMN end_date TEXT")

    c.execute("""
        CREATE TABLE IF NOT EXISTS contact_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            service TEXT,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS site_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT 'blue',
            tagline TEXT,
            description TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '[]',
            features TEXT NOT NULL DEFAULT '[]',
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS page_content (
            page TEXT NOT NULL,
            section TEXT NOT NULL,
            field TEXT NOT NULL,
            value TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (page, section, field)
        )
    """)

    # Seed default admin
    existing = c.execute("SELECT id FROM admin_users LIMIT 1").fetchone()
    if not existing:
        c.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ("admin", hash_password("cliffIT2026"))
        )

    # Seed default settings
    for key, val in DEFAULT_SETTINGS.items():
        existing = c.execute("SELECT key FROM site_settings WHERE key = ?", (key,)).fetchone()
        if not existing:
            c.execute("INSERT INTO site_settings (key, value) VALUES (?, ?)", (key, val))

    # Seed default services
    from app_services import DEFAULT_SERVICES, DEFAULT_SERVICE_ORDER
    for i, slug in enumerate(DEFAULT_SERVICE_ORDER):
        existing = c.execute("SELECT slug FROM services WHERE slug = ?", (slug,)).fetchone()
        if not existing:
            svc = DEFAULT_SERVICES[slug]
            c.execute("""
                INSERT INTO services (slug, title, color, tagline, description, details, features, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (slug, svc["title"], svc["color"], svc["tagline"], svc["description"],
                  json.dumps(svc["details"]), json.dumps(svc["features"]), i))

    # Seed default page content
    from page_content_defaults import DEFAULT_PAGE_CONTENT
    for (page, section, field), value in DEFAULT_PAGE_CONTENT.items():
        existing = c.execute(
            "SELECT value FROM page_content WHERE page=? AND section=? AND field=?",
            (page, section, field)
        ).fetchone()
        if not existing:
            c.execute(
                "INSERT INTO page_content (page, section, field, value) VALUES (?, ?, ?, ?)",
                (page, section, field, value)
            )

    conn.commit()
    conn.close()

# ─── Page Content ───

def get_page_content(page):
    """Return all content for a page as {section: {field: value}}."""
    conn = get_db()
    rows = conn.execute(
        "SELECT section, field, value FROM page_content WHERE page = ?", (page,)
    ).fetchall()
    conn.close()
    result = {}
    for r in rows:
        result.setdefault(r["section"], {})[r["field"]] = r["value"]
    return result

def update_page_content(page, data):
    """Update page content from flat dict like 'section__field' -> value."""
    conn = get_db()
    for key, value in data.items():
        if "__" in key:
            section, field = key.split("__", 1)
            conn.execute(
                "INSERT OR REPLACE INTO page_content (page, section, field, value) VALUES (?, ?, ?, ?)",
                (page, section, field, str(value))
            )
    conn.commit()
    conn.close()

# ─── Site Settings ───

def get_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM site_settings").fetchall()
    conn.close()
    settings = dict(DEFAULT_SETTINGS)
    for r in rows:
        settings[r["key"]] = r["value"]
    return settings

def update_settings(data):
    conn = get_db()
    for key, val in data.items():
        conn.execute("INSERT OR REPLACE INTO site_settings (key, value) VALUES (?, ?)", (key, str(val)))
    conn.commit()
    conn.close()

# ─── Services ───

def get_all_services():
    conn = get_db()
    rows = conn.execute("SELECT * FROM services ORDER BY sort_order").fetchall()
    conn.close()
    result = {}
    order = []
    for r in rows:
        slug = r["slug"]
        order.append(slug)
        result[slug] = {
            "title": r["title"],
            "color": r["color"],
            "tagline": r["tagline"] or "",
            "description": r["description"],
            "details": json.loads(r["details"]) if r["details"] else [],
            "features": json.loads(r["features"]) if r["features"] else [],
            "is_active": r["is_active"],
        }
    return result, order

def get_service(slug):
    conn = get_db()
    r = conn.execute("SELECT * FROM services WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    if not r:
        return None
    return {
        "slug": r["slug"], "title": r["title"], "color": r["color"],
        "tagline": r["tagline"] or "", "description": r["description"],
        "details": json.loads(r["details"]) if r["details"] else [],
        "features": json.loads(r["features"]) if r["features"] else [],
        "is_active": r["is_active"], "sort_order": r["sort_order"],
    }

def update_service(slug, data):
    conn = get_db()
    conn.execute("""
        UPDATE services SET title=?, color=?, tagline=?, description=?,
            details=?, features=?, is_active=?
        WHERE slug=?
    """, (data["title"], data["color"], data.get("tagline",""),
          data["description"], json.dumps(data.get("details", [])),
          json.dumps(data.get("features", [])),
          data.get("is_active", 1), slug))
    conn.commit()
    conn.close()

# ─── Jobs ───

def get_active_jobs(category=None, location=None):
    conn = get_db()
    query = "SELECT * FROM jobs WHERE is_active = 1"
    params = []
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if location and location != "All":
        query += " AND location = ?"
        params.append(location)
    query += " ORDER BY created_at DESC"
    jobs = conn.execute(query, params).fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = get_db()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return job

def create_job(data):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO jobs (title, location, job_type, category, experience_level,
                         salary_range, description, requirements, benefits,
                         openings, end_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"], data["location"], data["job_type"], data["category"],
        data.get("experience_level", "Mid-Level"), data.get("salary_range", ""),
        data["description"], data.get("requirements", ""), data.get("benefits", ""),
        data.get("openings", 1), data.get("end_date") or None, now, now
    ))
    conn.commit()
    conn.close()

def update_job(job_id, data):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        UPDATE jobs SET title=?, location=?, job_type=?, category=?,
            experience_level=?, salary_range=?, description=?,
            requirements=?, benefits=?, openings=?, end_date=?,
            is_active=?, updated_at=?
        WHERE id=?
    """, (
        data["title"], data["location"], data["job_type"], data["category"],
        data.get("experience_level", "Mid-Level"), data.get("salary_range", ""),
        data["description"], data.get("requirements", ""), data.get("benefits", ""),
        data.get("openings", 1), data.get("end_date") or None,
        data.get("is_active", 1), now, job_id
    ))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_db()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def get_all_jobs():
    conn = get_db()
    jobs = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    conn.close()
    return jobs

def save_contact(data):
    conn = get_db()
    conn.execute("""
        INSERT INTO contact_submissions (name, email, company, phone, service, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["name"], data["email"], data.get("company",""), data.get("phone",""),
          data.get("service",""), data["message"]))
    conn.commit()
    conn.close()

def get_contacts():
    conn = get_db()
    contacts = conn.execute("SELECT * FROM contact_submissions ORDER BY created_at DESC").fetchall()
    conn.close()
    return contacts

def get_job_categories():
    return ["Engineering", "Cloud & DevOps", "Cybersecurity", "Data & AI",
            "Design & UX", "Project Management", "QA & Testing", "Support"]

def get_job_locations():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT location FROM jobs WHERE is_active=1 ORDER BY location").fetchall()
    conn.close()
    return [r["location"] for r in rows] if rows else ["Austin, TX", "Remote", "New York, NY"]
