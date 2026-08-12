# PropVerify

**Authenticated Property Listing System with Multi-Stage Verification**

A complete Flask web application that lets property owners list properties only after their identity, ownership documents, and listings have all been approved by an administrator. Buyers can browse verified listings and message owners directly.

---

## Features

- **Authentication** — Register, login, logout, password hashing (Werkzeug), mock email verification.
- **Roles** — `admin`, `owner`, `user`, enforced via decorators on every protected route.
- **Multi-stage verification**
  - Identity: ID document upload → admin approval.
  - Property: ownership document upload → admin approval.
  - Listing: every listing must be approved before becoming public.
- **Property listings** — Full CRUD with multi-image upload; only verified owners can publish.
- **Admin dashboard** — Counts + queues for IDs, ownership docs, and listings; one-click approve/reject with notes; user role management.
- **Search & filtering** — Search by location, filter by price range and type, "verified only" toggle.
- **Messaging** — Inquiries from buyers to owners with inbox/sent views and read tracking.
- **Status badges** — `pending`/`approved`/`rejected` everywhere; green **Verified** badge on listings that pass all three checks.
- **Security** — Site-wide CSRF, file-extension whitelisting, randomized stored filenames, 16 MB upload cap, admin-only download of sensitive documents.

---

## Tech stack

| Layer       | Choice                                                    |
| ----------- | --------------------------------------------------------- |
| Backend     | Flask 3                                                   |
| Templates   | Jinja2 + Bootstrap 5 + Bootstrap Icons                    |
| Database    | SQLite via SQLAlchemy                                     |
| Auth        | Flask-Login (session-based)                               |
| Forms       | Flask-WTF + WTForms (with CSRF)                           |
| Migrations  | Flask-Migrate (Alembic)                                   |
| Uploads     | Local `uploads/` folder, validated by extension and size  |

---

## Project structure

```
.
├── app/
│   ├── __init__.py            # App factory + blueprint registration
│   ├── models.py              # User, Property, PropertyImage, Verification, Message
│   ├── forms.py               # WTForms with validation
│   ├── decorators.py          # role_required / admin_required / owner_required
│   ├── seed.py                # Default admin seeding
│   ├── template_helpers.py    # Jinja filters (currency, date, status_badge)
│   ├── routes/
│   │   ├── main.py            # Browse + search
│   │   ├── auth.py            # Register / login / logout / email verify
│   │   ├── properties.py      # Listing CRUD + ownership submission
│   │   ├── verifications.py   # Identity submission
│   │   ├── admin.py           # Admin dashboard, queues, decisions
│   │   ├── messages.py        # Inquiries / inbox
│   │   └── uploads.py         # Protected file serving
│   ├── services/
│   │   ├── file_service.py    # Safe file save + extension validation
│   │   └── email_service.py   # Mock console-based email sender
│   ├── static/
│   │   └── style.css
│   └── templates/             # base, auth/, properties/, verifications/, admin/, messages/
├── config.py                  # Configuration (reads .env / environment)
├── run.py                     # Entry point — `python run.py`
├── requirements.txt           # Python dependencies
├── .env.example               # Copy to `.env` and edit
├── .gitignore
├── README.md                  # You are here
└── USAGE.md                   # End-to-end usage walkthrough
```

`uploads/` and `app.db` are created automatically the first time you run the app.

---

## Getting started (local machine)

### 1. Requirements

- **Python 3.11+** (3.10 also works, but the project is developed against 3.11).
- pip (or another installer like uv / pipx).

### 2. Install

```bash
# clone or unzip the project, then:
cd propverify

python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set SESSION_SECRET to a long random string.
# (python -c "import secrets; print(secrets.token_hex(32))")
```

The app reads settings from real environment variables. You can either:

- `export` them in your shell (Linux/macOS) / `set` (Windows), **or**
- use any tool you already use for `.env` files (`direnv`, `dotenvx`, `python-dotenv`, etc.).

### 4. Run

```bash
python run.py
```

You should see:

```
[SEED] Created default admin: admin@example.com / Admin123!
 * Running on http://127.0.0.1:5000
```

Open <http://127.0.0.1:5000> in your browser.

### 5. Sign in as admin

| Field    | Value                |
| -------- | -------------------- |
| Email    | `admin@example.com`  |
| Password | `Admin123!`          |

(Override these by setting `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD` in `.env` **before** the first launch.)

---

## Database migrations (optional)

The app calls `db.create_all()` at boot, so you don't need migrations to start. For schema changes over time, use Flask-Migrate:

```bash
export FLASK_APP=run.py        # Windows: set FLASK_APP=run.py
flask db init                  # only the first time
flask db migrate -m "describe change"
flask db upgrade
```

---

## Resetting the database

To wipe everything and start over:

```bash
rm app.db
rm -rf uploads/ids uploads/ownership uploads/properties
python run.py
```

A fresh `app.db` and the seeded admin will be recreated.

---

## Running in production

For anything beyond local development, swap the Flask dev server for a real WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'run:app'
```

See **USAGE.md → Production checklist** for the rest (HTTPS, real DB, real email, durable file storage, strong secrets).

---

## Documentation

- **[USAGE.md](./USAGE.md)** — Full end-to-end walkthrough of every feature, plus admin operations and the verification flow.
- **[.env.example](./.env.example)** — All available environment variables.

---

## License

MIT — do whatever you want with it.
