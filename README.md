# Field Notes — Flask Blog
Jason Breedlove's Python blog, modernized from the original Flask learning project.

## Features
Accounts and login, editor-only post creation and editing, plain-text comments, CSRF-protected deletion, sanitized article HTML, and a responsive dark layout.

## Local development
Use Python 3.12, create a virtual environment, then:
```sh
pip install -r requirements-dev.txt
cp .env.example .env
# Set SECRET_KEY to a random value in .env before continuing.
flask --app app init-db
flask --app app create-editor
# Set ADMIN_USER_ID to the ID printed by create-editor.
flask --app app run
python -m pytest -q
```
No account becomes an administrator by registration order. ADMIN_USER_ID defaults to zero, granting nobody editorial access. The editor command securely prompts for a password in the terminal.

## Production on Vercel
Import Breedlove-Jason/flask_blog. Vercel supports the app.py Flask entrypoint; vercel.json selects Flask. No frontend build is required.

Configure these server-side environment variables:
- SECRET_KEY: a stable, randomly generated secret; never commit it.
- DATABASE_URL: persistent PostgreSQL connection string with SSL, supplied by your database provider.
- APP_ENV: production (enables secure session cookies).
- ADMIN_USER_ID: the editor account ID, after provisioning.

Initialize tables once against the production database with the Flask CLI, then provision the editor. Do not run schema initialization on every request. Existing databases require a backup and schema/data review before reuse. This version intentionally does not deploy the old committed SQLite database or migrate its accounts.

Local SQLite is for development only. PostgreSQL deployment has not yet been exercised. Public registration needs an abuse-control strategy before broader promotion; email verification and password reset are not implemented.

Suggested domain: blog.jasonbreedlove.dev.

## Verification
Six automated integration tests cover registration/login, explicit editor authorization (including a second registrant), author IDs, post editing, escaped comments, dependent comment deletion, CSRF, duplicate titles, and missing posts. Browser and hosted PostgreSQL verification remain pending.

## Changes
Removed broken Gravatar initialization, fixed author foreign keys, replaced hard-coded administrator ID, changed logout/deletion to POST, removed open referrer redirects and the nonworking PHP contact form, and replaced duplicated Bootstrap page shells with one base template. Rich text uses a plain textarea accepting a small HTML subset; no external editor scripts are required.

The original source and assets remain in Git history. Original third-party theme assets retain their existing attribution and terms.
