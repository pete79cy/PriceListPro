# Coolify deployment

This project is ready to run in Coolify with the included `Dockerfile`.

## What to create in Coolify

1. Create a new application from your Git repository.
2. Choose the Dockerfile-based deployment option.
3. Add a PostgreSQL service and connect it to the app.
4. Set the exposed application port to `5000`.
5. Set the health check path to `/healthcheck` or `/health`.

## Required environment variables

Copy the values from `./.env.coolify.example` and update at least:

- `DATABASE_URL`
- `SESSION_SECRET`
- `API_TOKEN`

`AUTH_MODE=local` is already the default inside the container, so the app no longer depends on Replit OIDC just to start.

## Recommended persistent storage

Mount a persistent volume to `/app/storage` if you want uploads and generated PDFs to survive redeploys.

These folders are also safe to persist when useful:

- `/app/storage`
- `/app/database_backups`
- `/app/exports`
- `/app/logs`

## Start behavior

The container starts with:

```bash
gunicorn main:app
```

and listens on `0.0.0.0:$PORT`.
