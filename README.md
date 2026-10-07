# JEE Mock Test — Render + PostgreSQL + Groq

## Required secret
Only one external API secret is required by this version:
`GROQ_API_KEY`

Render provides the PostgreSQL connection string automatically from `render.yaml`.

## Deploy
1. Put this folder in a GitHub repository.
2. Create a Groq API key.
3. In Render choose **New -> Blueprint** and select the repository.
4. Render reads `render.yaml`.
5. Enter `GROQ_API_KEY` when Render asks for it.
6. Deploy.

The Blueprint creates a Python web service and a PostgreSQL database.

## Database initialization
After the database is created, run `database/schema.sql` once against the Render PostgreSQL database. It creates the tables, enums, and initial JEE topics.

## API
Health:
`https://YOUR-API.onrender.com/health`

Topics:
`GET /api/topics?class_level=11th`

Generate:
`POST /api/generate-test`

Submit:
`POST /api/submit-test`

## Flutter
Use the deployed API URL as `API_BASE_URL`:
`flutter run --dart-define=API_BASE_URL=https://YOUR-API.onrender.com`

Never put `GROQ_API_KEY` inside Flutter or browser code.

## Important
This is a Render-ready development baseline. For a public production launch, add authentication, rate limiting, restricted CORS, migrations, monitoring, and stronger AI-question verification.
