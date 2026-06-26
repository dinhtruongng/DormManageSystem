# Deploying to PythonAnywhere (free tier, no card)

This guide gets the dorm demo live on a public `https://<username>.pythonanywhere.com`
URL at zero cost. PythonAnywhere's free tier runs the app under their managed WSGI
server with an SQLite database — no external services, no payment.

> Constraints of the free tier (fine for a demo): one web app, no always-on
> (the worker is suspended after ~3 months of inactivity and reloaded on first
> hit), ~512 MB disk, daily CPU seconds quota. Internet-public, real HTTPS.

## 0. Before you start — push the code to GitHub

PythonAnywhere clones straight from your repo. Your local code must be on GitHub
first. If you have not pushed the deploy prep yet, from this machine:

```bash
git add -A
git commit -m "Deploy prep: production settings, WhiteNoise, PythonAnywhere guide"
git push origin main
```

Repo: https://github.com/dinhtruongng/DormManageSystem

## 1. Create the account

1. Sign up at https://www.pythonanywhere.com/registration/signup/beginner
   (the free **Beginner** account — no card asked).
2. Your username becomes the URL: `<username>.pythonanywhere.com`. Pick it now.

## 2. Create a web app (Manual config)

1. Dashboard → **Web** tab → **Add a new web app** → **Next**.
2. Choose a **custom domain** (the free `username.pythonanywhere.com`) → **Next**.
3. **Manual configuration** → **Next**.
4. **Python version**: `3.11` (matches local dev) → **Next**.

This creates the web app entry and a placeholder WSGI config. Do NOT pick the
"Django" button — that installs an old Django. Manual lets us pin 5.0.7.

## 3. Pull the code

Open a **Bash console** (Dashboard → **Consoles** → **Bash**). Clone the repo
into your home directory:

```bash
git clone https://github.com/dinhtruongng/DormManageSystem.git ~/DormManageSystem
```

If your repo is private you will be asked for a GitHub username + Personal Access
Token (use a token, not your password).

## 4. Make a virtualenv and install deps

In the same Bash console:

```bash
cd ~/DormManageSystem
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure environment variables

PythonAnywhere does not read `.env` files unless we ask it to. Create one in the
app root (it is on the server only, not in git):

```bash
cd ~/DormManageSystem
cat > .env <<'EOF'
DJANGO_SECRET_KEY=change-this-to-a-long-random-string
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://<username>.pythonanywhere.com
EOF
```

Replace `<username>` with your PythonAnywhere username in both places, and put a
real random string in `DJANGO_SECRET_KEY` (e.g. run `python -c "import secrets;print(secrets.token_urlsafe(50))"`).

## 6. Migrate, collect static, seed

```bash
cd ~/DormManageSystem
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

`seed_demo` builds the demo dataset (24 students, 40 beds, 8 assignments, etc.).

## 7. Point the WSGI file at the project

Dashboard → **Web** tab → **Code** section → the **WSGI configuration file** link
(e.g. `/var/www/<username>_pythonanywhere_com_wsgi.py`). Open it, delete the
entire contents, and paste:

```python
import os
import sys

# Add the project so `dorm_system` is importable.
project_home = "/home/<username>/DormManageSystem"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load the .env we wrote in step 5.
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dorm_system.config.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `<username>` with your username, **Save**, and go back to the **Web** tab.

## 8. Set the virtualenv and static mapping on the Web tab

On the **Web** tab:

1. **Virtualenv**: enter `/home/<username>/DormManageSystem/.venv` (or use the
   picker).
2. **Static files** section → add a mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/<username>/DormManageSystem/staticfiles`

## 9. Reload and open

Click the green **Reload** button at the top of the **Web** tab, then visit:

```
https://<username>.pythonanywhere.com
```

You should see the login page. Demo accounts:

- `admin` / `admin` — Admin
- `finance` / `finance` — Finance
- `student01` / `student` — Student

## 10. Updating after a code change

In a Bash console:

```bash
cd ~/DormManageSystem
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Web** tab → **Reload**.

## Troubleshooting

- **500 error / blank page**: Dashboard → **Web** tab → **Error log** (top right
  of the Log files section). The most common cause is a wrong path in the WSGI
  file or a missing `.env` on line `DJANGO_ALLOWED_HOSTS`.
- **CSS missing (unstyled page)**: you skipped `collectstatic` (step 6) or the
  static mapping (step 8), or you forgot to **Reload**.
- **CSRF / login form rejected**: `DJANGO_CSRF_TRUSTED_ORIGINS` and
  `DJANGO_ALLOWED_HOSTS` in `.env` still contain the literal `<username>`
  placeholder — fill in your real username.
- **"DisallowedHost"**: `DJANGO_ALLOWED_HOSTS` doesn't list your
  `username.pythonanywhere.com`. Add it (comma-separated, no scheme).

## Why this satisfies the report's deployment design

The report targets PostgreSQL + S3-compatible storage for production. The demo
keeps both swappable behind environment variables (`DATABASE_URL` for Postgres,
the storage backend is isolated) so the same code runs on SQLite + local media
locally and on PythonAnywhere, and can switch to Postgres/S3 for a real
deployment without code changes — see `docs/report-updates/implementation-decisions.md`.
