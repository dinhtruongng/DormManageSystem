# Demo Validation Notes

Use this file to summarize implementation validation and visual QA.

## Smoke checks

| Date | Command / check | Result | Notes |
|---|---|---|---|
| 2026-06-26 | `uv run python manage.py check` | 0 issues | All apps and URLs load. |
| 2026-06-26 | `uv run python manage.py migrate` | OK | All migrations apply (SQLite default). |
| 2026-06-26 | `uv run python manage.py seed_demo` | 24 students, 40 beds, 8 assignments, 6 invoices, 2 payments | FR-14 seed. |
| 2026-06-26 | Admin role: every HTML route returns 200 | Pass | Dashboard, students, rooms, billing, payments review, announcements, reports, audit. |
| 2026-06-26 | Student role denied staff routes (dashboard, payment review) | 403 | Negative access control (NFR-01). |
| 2026-06-26 | Finance confirms pending payment #1 via UI | invoice `issued`→`paid`, outstanding 3,000,000→0, audit row written | End-to-end payment review (FR-10, NFR-02, NFR-07). |
| 2026-06-26 | `GET /api/v1/dashboard-summary` | `{success:true,...}` envelope | API contract (§8.7). |

## Visual QA passes

| Date | Agent | URL | Result | Remaining issues |
|---|---|---|---|---|
| 2026-06-26 | visual-qa | http://localhost:8000 | Not ready → fixed | Blocker: status badges rendered as escaped HTML. Fixed by marking the `status_badge` template filter output `safe`. Minor: favicon 404, sidebar naming, "Rooms detail" grammar — all fixed. |
| 2026-06-26 | visual-qa | report PDF pages 32/33/44/45/46 | Ready (after fix) | Initial pass flagged a caption mismatch, but that was a hallucinated caption/bibliography not present in the report; verified source captions match the rendered PDF. Figure scaling and placement are correct. |

## App UI fixes applied this pass

- `status_badge` filter now returns `mark_safe(...)` — badges render as colored Bootstrap pills everywhere.
- Added inline SVG favicon to `base.html` to remove the console 404.
- Sidebar links renamed: "Buildings" (`/rooms/`) and "Rooms" (`/rooms/rooms/`).
- Login demo-account hint corrected from `student` to `student01` (matches seeded accounts).

## Report fixes applied this pass

- Replaced §8.7 dashboard placeholder wireframe with `figures/screenshots/02-dashboard.png`.
- Replaced §8.8 payment-review placeholder wireframe with `figures/screenshots/05-payment-review.png`.
- Added Appendix A "Implemented Screens" with login, assignment, payment-upload, and check-out screenshots.
- Rewrote §8.1 and §8.6 framing text from "placeholder / before implementation" to "implemented".

## Report↔implementation consistency pass (2026-06-27)

Goal: ensure every report requirement has matching code. Findings and fixes:

| Area | Report reference | Was | Now |
|---|---|---|---|
| Student CSV import | FR-02, §8.10, §9.2 | No CSV anywhere | `import_students` service + admin `/residents/import/` view + "Import CSV" button |
| Student create API | §8.7 table row | No route for `POST /students` | `POST /api/v1/students/create` (Admin-only, 201/409) |
| Room inventory service | §9.1 map, §9.4 | No `rooms/services.py`; app read-only | `create_room`, `sync_beds`, `set_bed_status` (validated transitions + audit) |
| Recurring rent | §9.1, §9.7 | Logic inline in API handler | `generate_recurring_rent(period_label)` service; API calls it |
| Report CSV export | FR-12, §8.10, §9.10 | No exports | `/reports/{occupancy,finance}/export/` CSV views + buttons |

Smoke checks this pass (Django test client against seeded DB):

| Check | Result |
|---|---|
| CSV import (4-row file: 2 new, 1 dup, 1 invalid) via `POST /residents/import/` | 302; 2 students created, dup + invalid skipped |
| `POST /api/v1/students/create` (admin) | 201, record created |
| `POST /api/v1/students/create` duplicate code | 409 conflict |
| `POST /api/v1/students/create` as student | 403 (Admin-only enforced) |
| `POST /api/v1/invoices/batches` | 200, "Generated 6 recurring invoice(s)" (routes through service) |
| `GET /reports/occupancy/export/` | 200, `text/csv`, correct header row |
| `GET /reports/finance/export/` | 200, CSV with per-invoice receivable rows |
| Student denied `/residents/import/` | 403 |
| `create_room` (cap 2 / cap 4) | beds provisioned: 2 / 4 |
| `sync_beds` (4→6, 6→2) | beds added to 6; capacity updated to 2, no beds dropped |
| `set_bed_status` available→reserved | transition applied, `AuditLog` row written |
| `set_bed_status` reserved→cleaning (illegal) | `BedStatusError` raised |

System check: 0 issues. `makemigrations --check --dry-run`: no changes (all additions are rows/views/services, no schema change). `flush` + `seed_demo`: 24 students, 40 beds, 8 assignments, 6 invoices, 2 payments.
