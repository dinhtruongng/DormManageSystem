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
