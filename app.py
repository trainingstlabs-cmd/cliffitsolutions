#!/usr/bin/env python3
"""
cliffIT Solutions - Web Application
Uses Python stdlib http.server + Jinja2 (no Flask needed)
"""
import os
import json
import uuid
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from http.cookies import SimpleCookie
from jinja2 import Environment, FileSystemLoader, select_autoescape
import database as db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 5500))

# Sessions stored in memory  {session_id: {data}}
sessions = {}

# ─── Jinja2 Setup ───
env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape(["html"]),
)


# ─── URL Builder ───

def url_for(endpoint, **kwargs):
    routes = {
        "home": "/", "services": "/services", "about": "/about",
        "industries": "/industries", "careers": "/careers", "contact": "/contact",
        "admin_login": "/admin/login", "admin_logout": "/admin/logout",
        "admin_dashboard": "/admin", "admin_new_job": "/admin/jobs/new",
        "admin_settings": "/admin/settings", "admin_services": "/admin/services",
        "admin_pages": "/admin/pages",
    }
    if endpoint == "service_detail":
        return f"/services/{kwargs.get('slug', '')}"
    if endpoint == "job_detail":
        return f"/careers/{kwargs.get('job_id', '')}"
    if endpoint == "admin_edit_job":
        return f"/admin/jobs/{kwargs.get('job_id', '')}/edit"
    if endpoint == "admin_delete_job":
        return f"/admin/jobs/{kwargs.get('job_id', '')}/delete"
    if endpoint == "admin_toggle_job":
        return f"/admin/jobs/{kwargs.get('job_id', '')}/toggle"
    if endpoint == "admin_edit_service":
        return f"/admin/services/{kwargs.get('slug', '')}/edit"
    if endpoint == "admin_edit_page":
        return f"/admin/pages/{kwargs.get('page', '')}"
    if endpoint == "static":
        return f"/static/{kwargs.get('filename', '')}"
    return routes.get(endpoint, "/")


class RequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with routing."""

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

    # ─── Session helpers ───

    def _get_sid(self):
        """Get session ID from cookie, or None."""
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        sid_cookie = cookie.get("session_id")
        if sid_cookie and sid_cookie.value in sessions:
            return sid_cookie.value
        return None

    def _ensure_session(self):
        """Get or create session. Returns (sid, session_dict)."""
        sid = self._get_sid()
        if sid:
            return sid, sessions[sid]
        sid = str(uuid.uuid4())
        sessions[sid] = {}
        return sid, sessions[sid]

    def get_session(self):
        sid = self._get_sid()
        if sid:
            return sessions[sid]
        return {}

    # ─── Response helpers ───

    def send_html(self, html, code=200, sid=None):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if sid:
            self.send_header("Set-Cookie", f"session_id={sid}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def send_redirect(self, location, sid=None):
        self.send_response(302)
        self.send_header("Location", location)
        if sid:
            self.send_header("Set-Cookie", f"session_id={sid}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()

    def render(self, template_name, **kwargs):
        sid, sess = self._ensure_session()
        # Pop flashes (one-time display)
        flashes = sess.pop("_flashes", [])
        kwargs["session"] = sess
        kwargs["request"] = self
        kwargs["url_for"] = url_for
        kwargs["site"] = db.get_settings()
        kwargs["get_flashed_messages"] = lambda with_categories=False: flashes if with_categories else [m for _, m in flashes]
        tmpl = env.get_template(template_name)
        html = tmpl.render(**kwargs)
        return html, sid

    def flash(self, message, category="success"):
        sid, sess = self._ensure_session()
        sess.setdefault("_flashes", []).append((category, message))
        return sid

    def parse_form(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = {}
        for pair in body.split("&"):
            if "=" in pair:
                key, val = pair.split("=", 1)
                data[unquote(key.replace("+", " "))] = unquote(val.replace("+", " "))
        return data

    def serve_static(self, path):
        static_path = os.path.join(BASE_DIR, "static", path)
        if not os.path.isfile(static_path):
            self.send_error(404)
            return
        ext = os.path.splitext(path)[1]
        content_types = {
            ".css": "text/css", ".js": "application/javascript",
            ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
            ".ico": "image/x-icon", ".woff2": "font/woff2",
        }
        ct = content_types.get(ext, "application/octet-stream")
        with open(static_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(data))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(data)

    @property
    def endpoint(self):
        path = urlparse(self.path).path
        routes = {
            "/": "home", "/services": "services", "/about": "about",
            "/industries": "industries", "/careers": "careers", "/contact": "contact",
        }
        if path in routes:
            return routes[path]
        if path.startswith("/services/"):
            return "service_detail"
        if path.startswith("/careers/") and path.split("/")[-1].isdigit():
            return "job_detail"
        return ""

    # ─── GET Router ───

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.startswith("/static/"):
            self.serve_static(path[8:])
            return

        try:
            if path == "/":
                self.handle_home()
            elif path == "/services":
                self.handle_services()
            elif path.startswith("/services/") and len(path.split("/")) == 3:
                self.handle_service_detail(path.split("/")[2])
            elif path == "/about":
                self.handle_about()
            elif path == "/industries":
                self.handle_industries()
            elif path == "/careers":
                self.handle_careers(query)
            elif re.match(r"^/careers/(\d+)$", path):
                self.handle_job_detail(int(re.match(r"^/careers/(\d+)$", path).group(1)))
            elif path == "/contact":
                self.handle_contact_get(query)
            elif path == "/admin/login":
                self.handle_admin_login_get()
            elif path == "/admin/logout":
                self.handle_admin_logout()
            elif path == "/admin":
                self.handle_admin_dashboard()
            elif path == "/admin/jobs/new":
                self.handle_admin_new_job_get()
            elif re.match(r"^/admin/jobs/(\d+)/edit$", path):
                self.handle_admin_edit_job_get(int(re.match(r"^/admin/jobs/(\d+)/edit$", path).group(1)))
            elif path == "/admin/settings":
                self.handle_admin_settings_get()
            elif path == "/admin/services":
                self.handle_admin_services_get()
            elif re.match(r"^/admin/services/([^/]+)/edit$", path):
                self.handle_admin_edit_service_get(re.match(r"^/admin/services/([^/]+)/edit$", path).group(1))
            elif path == "/admin/pages":
                self.handle_admin_pages_list()
            elif re.match(r"^/admin/pages/([a-z]+)$", path):
                self.handle_admin_edit_page_get(re.match(r"^/admin/pages/([a-z]+)$", path).group(1))
            else:
                self.send_error(404)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_error(500, str(e))

    # ─── POST Router ───

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/contact":
                self.handle_contact_post()
            elif path == "/admin/login":
                self.handle_admin_login_post()
            elif path == "/admin/jobs/new":
                self.handle_admin_new_job_post()
            elif re.match(r"^/admin/jobs/(\d+)/edit$", path):
                self.handle_admin_edit_job_post(int(re.match(r"^/admin/jobs/(\d+)/edit$", path).group(1)))
            elif re.match(r"^/admin/jobs/(\d+)/delete$", path):
                self.handle_admin_delete_job(int(re.match(r"^/admin/jobs/(\d+)/delete$", path).group(1)))
            elif re.match(r"^/admin/jobs/(\d+)/toggle$", path):
                self.handle_admin_toggle_job(int(re.match(r"^/admin/jobs/(\d+)/toggle$", path).group(1)))
            elif path == "/admin/settings":
                self.handle_admin_settings_post()
            elif re.match(r"^/admin/services/([^/]+)/edit$", path):
                self.handle_admin_edit_service_post(re.match(r"^/admin/services/([^/]+)/edit$", path).group(1))
            elif re.match(r"^/admin/pages/([a-z]+)$", path):
                self.handle_admin_edit_page_post(re.match(r"^/admin/pages/([a-z]+)$", path).group(1))
            else:
                self.send_error(404)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.send_error(500, str(e))

    # ─── Public Handlers ───

    def _get_services(self):
        services, order = db.get_all_services()
        active = {k: v for k, v in services.items() if v.get("is_active", 1)}
        active_order = [s for s in order if s in active]
        return active, active_order

    def handle_home(self):
        services, order = self._get_services()
        featured_jobs = db.get_active_jobs()[:3]
        pc = db.get_page_content("home")
        html, sid = self.render("index.html", services=services, service_order=order,
                                featured_jobs=featured_jobs, pc=pc)
        self.send_html(html, sid=sid)

    def handle_services(self):
        services, order = self._get_services()
        pc = db.get_page_content("services")
        html, sid = self.render("services.html", services=services, service_order=order, pc=pc)
        self.send_html(html, sid=sid)

    def handle_service_detail(self, slug):
        services, order = self._get_services()
        svc = services.get(slug)
        if not svc:
            self.send_redirect("/services")
            return
        html, sid = self.render("service_detail.html", service=svc, slug=slug,
                                services=services, service_order=order)
        self.send_html(html, sid=sid)

    def handle_about(self):
        pc = db.get_page_content("about")
        html, sid = self.render("about.html", pc=pc)
        self.send_html(html, sid=sid)

    def handle_industries(self):
        pc = db.get_page_content("industries")
        html, sid = self.render("industries.html", pc=pc)
        self.send_html(html, sid=sid)

    def handle_careers(self, query):
        category = query.get("category", ["All"])[0]
        location = query.get("location", ["All"])[0]
        jobs = db.get_active_jobs(
            category if category != "All" else None,
            location if location != "All" else None
        )
        categories = ["All"] + db.get_job_categories()
        locations = ["All"] + db.get_job_locations()
        pc = db.get_page_content("careers")
        html, sid = self.render("careers.html", jobs=jobs, categories=categories,
                                locations=locations, sel_category=category, sel_location=location, pc=pc)
        self.send_html(html, sid=sid)

    def handle_job_detail(self, job_id):
        job = db.get_job_by_id(job_id)
        if not job:
            self.send_redirect("/careers")
            return
        html, sid = self.render("job_detail.html", job=job)
        self.send_html(html, sid=sid)

    def handle_contact_get(self, query):
        services, order = self._get_services()
        selected_service = query.get("service", [""])[0]
        pc = db.get_page_content("contact")
        html, sid = self.render("contact.html", services=services, service_order=order,
                                selected_service=selected_service, pc=pc)
        self.send_html(html, sid=sid)

    def handle_contact_post(self):
        data = self.parse_form()
        db.save_contact({
            "name": data.get("name", ""), "email": data.get("email", ""),
            "company": data.get("company", ""), "phone": data.get("phone", ""),
            "service": data.get("service", ""), "message": data.get("message", "")
        })
        sid = self.flash("Thank you! We'll be in touch within 24 hours.", "success")
        self.send_redirect("/contact", sid=sid)

    # ─── Admin Handlers ───

    def _check_admin(self):
        sess = self.get_session()
        return sess.get("admin_logged_in", False)

    def handle_admin_login_get(self):
        if self._check_admin():
            self.send_redirect("/admin")
            return
        html, sid = self.render("admin/login.html")
        self.send_html(html, sid=sid)

    def handle_admin_login_post(self):
        data = self.parse_form()
        username = data.get("username", "")
        password = data.get("password", "")
        conn = db.get_db()
        user = conn.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and db.check_password(password, user["password_hash"]):
            # Create fresh session with admin flag
            sid = str(uuid.uuid4())
            sessions[sid] = {"admin_logged_in": True, "admin_user": username}
            self.send_redirect("/admin", sid=sid)
        else:
            sid = self.flash("Invalid credentials.", "error")
            self.send_redirect("/admin/login", sid=sid)

    def handle_admin_logout(self):
        sid = self._get_sid()
        if sid and sid in sessions:
            del sessions[sid]
        self.send_redirect("/")

    def handle_admin_dashboard(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        jobs = db.get_all_jobs()
        contacts = db.get_contacts()
        stats = {
            "total_jobs": len(jobs),
            "active_jobs": sum(1 for j in jobs if j["is_active"]),
            "total_contacts": len(contacts)
        }
        html, sid = self.render("admin/dashboard.html", jobs=jobs, contacts=contacts, stats=stats)
        self.send_html(html, sid=sid)

    def handle_admin_new_job_get(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        html, sid = self.render("admin/job_form.html", job=None, categories=db.get_job_categories())
        self.send_html(html, sid=sid)

    def handle_admin_new_job_post(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        data = self.parse_form()
        db.create_job({
            "title": data["title"], "location": data["location"],
            "job_type": data["job_type"], "category": data["category"],
            "experience_level": data.get("experience_level", "Mid-Level"),
            "salary_range": data.get("salary_range", ""),
            "description": data["description"],
            "requirements": data.get("requirements", ""),
            "benefits": data.get("benefits", "")
        })
        sid = self.flash("Job posted successfully!", "success")
        self.send_redirect("/admin", sid=sid)

    def handle_admin_edit_job_get(self, job_id):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        job = db.get_job_by_id(job_id)
        if not job:
            self.send_redirect("/admin")
            return
        html, sid = self.render("admin/job_form.html", job=job, categories=db.get_job_categories())
        self.send_html(html, sid=sid)

    def handle_admin_edit_job_post(self, job_id):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        data = self.parse_form()
        db.update_job(job_id, {
            "title": data["title"], "location": data["location"],
            "job_type": data["job_type"], "category": data["category"],
            "experience_level": data.get("experience_level", "Mid-Level"),
            "salary_range": data.get("salary_range", ""),
            "description": data["description"],
            "requirements": data.get("requirements", ""),
            "benefits": data.get("benefits", ""),
            "is_active": 1 if data.get("is_active") else 0
        })
        sid = self.flash("Job updated!", "success")
        self.send_redirect("/admin", sid=sid)

    def handle_admin_delete_job(self, job_id):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        db.delete_job(job_id)
        sid = self.flash("Job deleted.", "success")
        self.send_redirect("/admin", sid=sid)

    def handle_admin_toggle_job(self, job_id):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        job = db.get_job_by_id(job_id)
        if job:
            conn = db.get_db()
            conn.execute("UPDATE jobs SET is_active = ? WHERE id = ?",
                         (0 if job["is_active"] else 1, job_id))
            conn.commit()
            conn.close()
        self.send_redirect("/admin")

    # ─── Admin Settings ───

    def handle_admin_settings_get(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        settings = db.get_settings()
        html, sid = self.render("admin/settings.html", settings=settings)
        self.send_html(html, sid=sid)

    def handle_admin_settings_post(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        data = self.parse_form()
        db.update_settings(data)
        sid = self.flash("Settings updated!", "success")
        self.send_redirect("/admin/settings", sid=sid)

    # ─── Admin Services ───

    def handle_admin_services_get(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        services, order = db.get_all_services()
        html, sid = self.render("admin/services_list.html", services=services, service_order=order)
        self.send_html(html, sid=sid)

    def handle_admin_edit_service_get(self, slug):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        svc = db.get_service(slug)
        if not svc:
            self.send_redirect("/admin/services")
            return
        html, sid = self.render("admin/service_form.html", service=svc, slug=slug)
        self.send_html(html, sid=sid)

    def handle_admin_edit_service_post(self, slug):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        data = self.parse_form()
        # Parse features from numbered fields
        features = []
        i = 0
        while f"feat_title_{i}" in data:
            ft = data.get(f"feat_title_{i}", "").strip()
            fd = data.get(f"feat_desc_{i}", "").strip()
            if ft:
                features.append({"title": ft, "desc": fd})
            i += 1
        # Parse details (newline-separated paragraphs)
        details_raw = data.get("details", "")
        details = [p.strip() for p in details_raw.split("\n\n") if p.strip()]
        db.update_service(slug, {
            "title": data["title"],
            "color": data.get("color", "blue"),
            "tagline": data.get("tagline", ""),
            "description": data["description"],
            "details": details,
            "features": features,
            "is_active": 1 if data.get("is_active") else 0,
        })
        sid = self.flash(f"Service '{data['title']}' updated!", "success")
        self.send_redirect("/admin/services", sid=sid)


    # ─── Admin Page Content ───

    EDITABLE_PAGES = {
        "home": "Homepage",
        "about": "About Us",
        "services": "Services",
        "careers": "Careers",
        "contact": "Contact",
        "industries": "Industries",
    }

    def handle_admin_pages_list(self):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        html, sid = self.render("admin/pages_list.html",
                                editable_pages=self.EDITABLE_PAGES)
        self.send_html(html, sid=sid)

    def handle_admin_edit_page_get(self, page):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        if page not in self.EDITABLE_PAGES:
            self.send_redirect("/admin/pages")
            return
        content = db.get_page_content(page)
        html, sid = self.render("admin/page_edit.html",
                                page=page,
                                page_title=self.EDITABLE_PAGES[page],
                                content=content)
        self.send_html(html, sid=sid)

    def handle_admin_edit_page_post(self, page):
        if not self._check_admin():
            self.send_redirect("/admin/login")
            return
        if page not in self.EDITABLE_PAGES:
            self.send_redirect("/admin/pages")
            return
        data = self.parse_form()
        db.update_page_content(page, data)
        sid = self.flash(f"'{self.EDITABLE_PAGES[page]}' page content updated!", "success")
        self.send_redirect(f"/admin/pages/{page}", sid=sid)


def main():
    db.init_db()
    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    print(f"""
╔══════════════════════════════════════════════╗
║   cliffIT Solutions - Web Server Running     ║
╠══════════════════════════════════════════════╣
║                                              ║
║   Website:  http://localhost:{PORT}            ║
║   Admin:    http://localhost:{PORT}/admin/login ║
║                                              ║
║   Admin Credentials:                         ║
║     Username: admin                          ║
║     Password: cliffIT2026                    ║
║                                              ║
║   Press Ctrl+C to stop                       ║
╚══════════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
