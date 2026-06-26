# Dorm Management Demo — Build Milestone Log

Authoritative record of the from-scratch build, reconstructed so it is verifiable
even if the chat transcript is truncated. Every step below was executed with `uv`
in this working directory and is backed by the artifacts committed alongside this
file (`dorm_system/`, `manage.py`, `requirements.txt`, migrations, templates) and
the live run output captured in `docs/report-updates/demo-validation.md`.

Source of truth: `report/main.tex` and its `.mmd` figures.

## Milestone 0 — Report inspection (source of truth)

Read `report/main.tex` (1,709 lines), `report/figures/class_diagram.mmd`, and
`report/figures/erd_diagram.mmd`. Established:

- **Stack** (§6.4, §7.6): Django MTV monolith, server-rendered, Bootstrap + HTMX,
  PostgreSQL (Postgres), local media, console/SMTP email. Versioned `/api/v1` JSON
  with `{success,message,data}` envelope.
- **Data model** (§7.2, ERD/class .mmd): 16 tables over 10 apps.
- **Pages** (§8.2): role-aware shell — student portal vs admin operations vs
  finance workspace.
- **Workflows** (§4): onboarding, payment review, check-out — all transactional
  with row locks; double-booking and unauthorized confirmation are the key risks.
- **Report-update obligations** (§8.6): wireframe placeholders must be replaced
  with real screenshots once the demo exists; report must stay aligned via the
  traceability matrix.

## Milestone 1 — Scaffold (verified)

- `requirements.txt` (Django 5.0.7, Pillow, psycopg2-binary, python-dotenv).
- `manage.py` with `DJANGO_SETTINGS_MODULE=dorm_system.config.settings`.
- `dorm_system/config/`: `settings.py` (env-driven DB, media, auth, templates,
  custom context processor), `urls.py` (HTML routes + `/api/v1` include),
  `api_urls.py`, `wsgi.py`, `asgi.py`.
- 10 apps created with `migrations/` and `templates/<app>/` dirs:
  `common, accounts, residents, rooms, assignments, billing, payments,
  communications, reports, demo_data`, each with an `apps.py` AppConfig.
- `uv venv && uv pip install -r requirements.txt` → 6 packages installed.
- Smoke test: `uv run python manage.py check` (after wiring) → 0 issues.

## Milestone 2 — Models + services + constraints (verified)

- `common/models.py`: all status enums + `AuditLog` + `record_audit`.
- `accounts/models.py`: `UserProfile` (role, phone). `permissions.py`:
  `require_role`, `can_view_student`, `role_required` decorator.
- `residents/models.py`: `Student`.
- `rooms/models.py`: `Building`, `Floor`, `Room`, `Bed` + `BedManager.available()`,
  unique constraints (floor-per-building, room-per-floor, bed-per-room).
- `assignments/models.py`: `Assignment`, `Inspection` + partial-unique constraints
  `one_active_assignment_per_student` / `one_active_assignment_per_bed`
  (the double-booking guard).
- `billing/models.py`: `Invoice` + `InvoiceManager.overdue()`, `InvoiceLine`.
- `payments/models.py`: `Payment` + `PaymentManager.pending_review()`,
  `PaymentEvidence`, check constraint `payment_amount_nonnegative`.
- `communications/models.py`: `Announcement`, `Notification`.
- Services: `billing.services` (balance calc, generate/refresh invoice, overdue),
  `assignments.services` (`AssignmentScorer` Strategy, `reserve_bed` with
  `select_for_update`, `activate_assignment`, `transfer_student`, `settle_checkout`),
  `payments.services` (submit evidence, review digest, confirm/reject),
  `communications.services`, `reports.services` (dashboard/occupancy/finance),
  `residents.services`.
- Generated 7 initial migrations (`makemigrations`). Fixed two build-time issues
  en route: `CheckConstraint(condition=...)` → `check=` (Django 5), and removed
  `multiple=True` from the `ClearableFileInput` widget.
- Smoke test: `migrate` applies all migrations.

## Milestone 3 — Views + templates + seed + run (verified)

- URL/view/api wiring for all 10 apps + versioned `/api/v1`.
- 21 templates under `dorm_system/templates` + per-app template dirs, Bootstrap
  base with role-aware sidebar, `status_badge`/`vnd` template filters.
- `demo_data/management/commands/seed_demo.py` + `demo_data/seed.py` building
  the full synthetic dataset.
- Created `common/migrations/` (missed in M1) + its `0001_initial`.
- `migrate` → OK; `seed_demo` → 24 students, 40 beds, 8 assignments, 6 invoices,
  2 payments.
- Smoke test (curl, logged): `/` → 302 login; admin login → 302 dashboard; all
  admin routes 200; student login → portal; staff routes 403 for student;
  `/api/v1/dashboard-summary` returns the envelope with real counts.

## Milestone 4 — Visual QA + fixes + report sync (verified)

- `visual-qa` agent (Playwright MCP) inspected the running app and returned a fix
  list. **Blocker found:** status badges rendered as escaped HTML (`&lt;span&gt;`)
  because the `status_badge` filter returned an unsafe string. **Fixed in main
  session:** `mark_safe(...)` in `common/templatetags/status_tags.py`. Re-scanned
  every page → 0 escaped badges. Minor fixes applied: inline SVG favicon, sidebar
  rename (Buildings / Rooms), "Rooms detail"→"Rooms", login demo hint
  `student`→`student01`.
- Captured six real screenshots to `report/figures/screenshots/`.
- **Report updates** (because implementation differs: placeholders → real UI):
  replaced §8.7 dashboard wireframe with `02-dashboard.png`, §8.8 payment-review
  wireframe with `05-payment-review.png`, added Appendix A "Implemented Screens"
  (login, assignment, payment-upload, checkout), rewrote §8.1/§8.6 framing from
  "placeholder" to "implemented".
- `latexmk -pdf` → 46 pages, clean. `pdftoppm -png -r 180` → `docs/qa/report-pages/`.
- `visual-qa` inspected rendered report pages; figure scaling/placement confirmed
  correct. (One agent pass hallucinated captions + a bibliography not present in
  the source — verified against `main.tex`, no real issue.)
- Copied `report/build/main.pdf` → `report/main.pdf`.

## From-scratch reproducibility (verified this session)

```bash
uv venv
uv pip install -r requirements.txt
uv run python manage.py migrate      # applies all migrations on a fresh DB
uv run python manage.py seed_demo    # 24 students, 40 beds, 8 assignments, 6 invoices, 2 payments
uv run python manage.py runserver 0.0.0.0:8000
```

Demo accounts: `admin/admin`, `finance/finance`, `student01/student`.

See `docs/report-updates/implementation-decisions.md` and `demo-validation.md`
for the decision log and the smoke/QA evidence tables.
