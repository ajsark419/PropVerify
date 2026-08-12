# PropVerify — Usage Guide

End-to-end walkthrough of every feature, plus admin operations.

---

## 1. First boot

When you start the app for the first time, a default administrator account is created automatically:

| Field     | Value                |
| --------- | -------------------- |
| Email     | `admin@example.com`  |
| Password  | `Admin123!`          |
| Role      | `admin`              |

Change the password immediately in production by setting `DEFAULT_ADMIN_PASSWORD` in `.env` **before** the very first run, or by editing the user in code/CLI afterwards.

---

## 2. Roles

| Role    | What they can do                                                                  |
| ------- | --------------------------------------------------------------------------------- |
| `user`  | Browse listings, send inquiries, submit identity verification.                    |
| `owner` | Everything `user` can, plus create/edit/delete listings and submit ownership docs.|
| `admin` | Approve/reject identity, ownership, and listings; manage user roles.              |

You pick `user` or `owner` at registration. Only an admin can promote/demote between `user` and `owner` later (from **Admin → Users**).

---

## 3. Buyer / Renter flow (`user`)

1. **Register** with role *Buyer / Renter*.
2. Click the **mock email verification link** that prints in the terminal where the app is running.
3. Browse listings on the home page.
4. Use the search bar:
   - Text search by **location** (partial match, case-insensitive).
   - Filter by **property type**.
   - Filter by **min / max price**.
   - Toggle **"Verified only"** to hide listings without a verified owner + approved ownership doc.
5. Open a listing detail page.
6. Send an **inquiry** to the owner (subject + body). Inquiries appear in your **Sent** tab and the owner's **Inbox**.

---

## 4. Owner flow (`owner`)

1. **Register** with role *Property Owner*.
2. Click the verification link in the terminal.
3. Go to **Verify Identity** and upload an ID document (PNG/JPG/PDF, ≤ 16 MB).
4. Wait for an admin to approve. Until then you can create listings but they will be invisible to the public.
5. Go to **New Listing**:
   - Fill in title, description, price, location, type.
   - Attach one or more images.
6. The new listing starts as `pending` for both **listing approval** and **property verification**.
7. From **My Listings**, click **Submit docs** for the listing and upload an ownership document.
8. Wait for admin approval.

A listing is publicly visible once **listing\_status = approved**. It earns the green **Verified** badge only when **all three** are true:

- Owner identity = approved
- Property verification = approved
- Listing status = approved

---

## 5. Admin flow (`admin`)

Sign in with the seeded admin account, then click **Admin** in the navbar.

The admin dashboard shows quick counts and links to four queues:

### 5.1 Users
- See every user, their role, email-verification state, identity-verification state, and join date.
- Toggle a user's role between `user` and `owner` from this page.

### 5.2 Identity Verifications
- Each row shows the submitter, submission date, and a **View** button to open the uploaded document (admins only — others get a 403).
- Approve or reject inline. Optional **note** is stored against the verification record.
- Approving sets `User.identity_verified = True`. Rejecting sets it back to `False`.

### 5.3 Property (Ownership) Verifications
- Same shape as identity, but tied to a specific property.
- Approving sets the listing's `property_verification_status = approved`.

### 5.4 Listings Approval
- **Pending** listings on top, then **Reviewed** below.
- Approving makes the listing publicly visible.
- Rejecting (or **Revoking** an already-approved listing) removes it from public browse immediately.

---

## 6. Status fields cheat sheet

Three independent status tracks per listing:

| Track                   | Field                                  | Set by   |
| ----------------------- | -------------------------------------- | -------- |
| Listing approval        | `Property.listing_status`              | Admin    |
| Property verification   | `Property.property_verification_status`| Admin    |
| Owner identity          | `User.identity_verified`               | Admin    |

Each can be `pending`, `approved`, or `rejected`. The "Verified" badge requires all three to be `approved`.

---

## 7. File uploads

- Stored on disk under `uploads/`:
  - `uploads/ids/`         — identity documents (admin-only download)
  - `uploads/ownership/`   — ownership documents (admin-only download)
  - `uploads/properties/`  — listing photos (publicly readable through `/files/properties/<name>`)
- Filenames are randomized (`secrets.token_hex(16).ext`) to prevent guessing.
- Allowed extensions:
  - Documents: `png`, `jpg`, `jpeg`, `pdf`
  - Images:    `png`, `jpg`, `jpeg`, `gif`, `webp`
- Max file size: **16 MB** (configurable in `config.py`).

---

## 8. Email verification

This is a **mock** email system. Instead of sending real email, the app prints the verification link to the server console:

```
======================================================================
[MOCK EMAIL] To: jane@example.com
[MOCK EMAIL] Click to verify: http://localhost:5000/auth/verify-email?token=...
======================================================================
```

To re-send the link for the currently signed-in user, click the **Resend** button in the yellow banner at the top of every page (shown until the email is verified).

To plug in a real email backend, replace `app/services/email_service.py:send_verification_email` with an SMTP / SendGrid / SES call.

---

## 9. Database & migrations

- Default DB is **SQLite** at `app.db` in the project root.
- On startup, `db.create_all()` is invoked, so a fresh checkout works without any extra commands.
- For schema changes, use **Flask-Migrate**:
  ```bash
  export FLASK_APP=run.py
  flask db init                 # only the first time
  flask db migrate -m "describe change"
  flask db upgrade
  ```
- Want PostgreSQL or MySQL? Change `SQLALCHEMY_DATABASE_URI` in `config.py`.

---

## 10. Useful URLs

| Path                                  | Purpose                                  |
| ------------------------------------- | ---------------------------------------- |
| `/`                                   | Browse / search listings                 |
| `/auth/register`                      | Create an account                        |
| `/auth/login`                         | Sign in                                  |
| `/auth/logout`                        | Sign out                                 |
| `/verifications/identity`             | Submit ID document                       |
| `/properties/mine`                    | Owner's listings                         |
| `/properties/new`                     | Create a listing                         |
| `/properties/<id>`                    | Listing detail + inquiry form            |
| `/properties/<id>/edit`               | Edit listing (re-enters pending state)   |
| `/properties/<id>/verify`             | Submit ownership document                |
| `/messages/inbox`                     | Inbox + sent messages                    |
| `/admin/`                             | Admin dashboard (counts + quick links)   |
| `/admin/users`                        | Manage users                             |
| `/admin/verifications/identity`       | Identity queue                           |
| `/admin/verifications/property`       | Ownership queue                          |
| `/admin/listings`                     | Listing approvals                        |

---

## 11. Production checklist

If you ever publish this beyond local development:

- [ ] Set a strong, unique `SESSION_SECRET`.
- [ ] Change `DEFAULT_ADMIN_PASSWORD` (or delete the seeded admin and create a new one).
- [ ] Switch the dev server to a production WSGI server: `gunicorn -w 4 -b 0.0.0.0:5000 'run:app'`.
- [ ] Move `SQLALCHEMY_DATABASE_URI` to a managed Postgres / MySQL connection string.
- [ ] Move `uploads/` to durable storage (S3, GCS) or at least a mounted volume.
- [ ] Replace the mock `send_verification_email` with a real provider.
- [ ] Put the app behind HTTPS (TLS terminating reverse proxy).
