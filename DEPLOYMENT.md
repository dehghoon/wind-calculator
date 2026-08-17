# Deployment

## Vercel Production Setup

This repository deploys as a multi-service Vercel project:

- `web/` runs the Next.js client.
- `backend/index.py` exposes the FastAPI application.
- `vercel.json` routes `/api/*` to the FastAPI service and `/*` to the web service.

## Project Settings


1. Import `dehghoon/wind-calculator`.
2. Keep the Vercel Root Directory at the repository root (`.`).
3. Do not set `web/` as the Vercel Root Directory.
4. Do not set `NEXT_PUBLIC_API_BASE_URL` to `localhost`. For the single-deployment setup, leave it unset so the web client uses same-origin `/api/...` requests.
5. Redeploy from the latest `main` commit.

## Verification

After a successful deployment, verify the API before using the calculator:

```text
https://<production-domain>/api/v1/capabilities
```

Expected result: JSON containing the supported routes, code editions, and engineering limitations.

## Separate API Hosting

If the FastAPI service is later deployed on a separate host, set:

```text
NEXT_PUBLIC_API_BASE_URL=https://<api-domain>
API_ALLOWED_ORIGINS=https://<web-domain>

```

Do not commit real secrets or provider credentials.