Deployment and Production Notes for Clyst

Overview
--------
This file documents how to deploy Clyst to Vercel (serverless) or a standard VM/container, plus required environment variables and optional features (S3 uploads, Firebase Admin, Postgres).

Important notes
---------------
- Vercel functions have a bundle size limit (500 MB). Heavy ML/image libs (SciPy/OpenCV), `firebase-admin`, and migration toolchains were removed from the default `requirements.txt` to keep the bundle small.
- Optional features (S3 uploads, Firebase Admin) are enabled by environment variables. Install optional packages like `boto3` or `firebase-admin` only when you need them.

Environment variables
---------------------
Minimum for basic operation:
- `FLASK_ENV=production` (set in vercel.json)
- `FLASK_SECRET_KEY` - secret for session management

Optional (recommended for production):
- `DATABASE_URL` - Postgres connection string (e.g. `postgresql://user:pass@host:5432/dbname`). When set, the app will use Postgres instead of local SQLite.
- `S3_BUCKET` - S3 bucket name to enable S3-backed uploads. When set, uploads will be stored in S3 and the user record will store the public URL.
- `S3_REGION` or `AWS_REGION` - AWS region for bucket (e.g. `us-east-1`).
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - credentials for S3 access.
- `GOOGLE_APPLICATION_CREDENTIALS` - path to service account JSON if you want `firebase-admin` to initialize on startup (not required; app falls back to REST verification).

Vercel-specific notes
---------------------
- Entrypoint: `api/index.py` is used as the WSGI entrypoint by `vercel.json`.
- `vercel.json` sets `FLASK_ENV=production` so the app picks production settings.
- If your deployment exceeds the 500 MB function limit, either:
  - Use: `vercel deploy --functions-beta` to enable extended limits (up to 1 GB), or
  - Split heavy workloads (advanced image analysis) into separate services/functions.

Running locally
---------------
1. Create a venv and install dependencies:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```
2. Create `.env` with required secrets (or set in environment).
3. Run the app locally:
```bash
flask run
# or
python app.py
```
4. Run smoke tests:
```bash
python -m compileall -q .
python tests\smoke_test.py
```

Migrations
----------
- The default deployment does not include migration tooling to keep the bundle small. To run migrations locally or on a dedicated deployment environment, install `Flask-Migrate` and `alembic` and run:
```bash
pip install Flask-Migrate alembic
export FLASK_APP=app.py
flask db init   # only once
flask db migrate
flask db upgrade
```

S3 uploads
----------
- To enable S3 uploads, set `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and optionally `S3_REGION`.
- The app will upload files to S3 and store public URLs in the DB. Local filesystem is used as a fallback and temporary staging location.
- `boto3` is included in `requirements.txt` so S3 works on deployment when enabled.

Firebase
--------
- The app falls back to Firebase REST-based token verification if `firebase-admin` is not present or not initialized.
- To enable `firebase-admin`, add the service account JSON and set `GOOGLE_APPLICATION_CREDENTIALS` to its path in the environment. Installing `firebase-admin` in production will enable the Admin SDK.

Troubleshooting
---------------
- Check Vercel function logs for full traceback if you see `FUNCTION_INVOCATION_FAILED` errors:
```bash
vercel logs <deployment-url> --since 1h
```
- If you get bundle size errors, remove optional heavy packages or deploy heavy features separately.

Contact
-------
If you want, I can:
- wire a managed Postgres connection and run DB migrations for you, or
- split heavy image analysis into a separate function, or
- prepare a PR with these changes.

*** End of file
