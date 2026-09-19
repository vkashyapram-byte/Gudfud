# GudFud Vercel Architecture & Deployment Rule

When working on GudFud, ALWAYS follow this architectural constraint to prevent breaking the live application:

## Monorepo Split Deployment
GudFud is deployed on Vercel as two distinct projects from a single GitHub repository:
1. **Frontend (`gudfud-web`)**: A Next.js application residing in `apps/web/`. It builds independently on Vercel. 
2. **Backend API (`gudfud-api`)**: A FastAPI application residing in `src/`. It runs on Vercel Serverless Functions using the `@vercel/python` builder. The configuration is defined in `vercel.json` at the root of the repository.

## Critical Deployment Gotchas
- **DO NOT overwrite the Backend**: Never deploy the API manually (e.g. `npx vercel`) from a temporary folder (e.g. `api_env` or `/tmp`). The backend must ONLY be deployed from the root of the repository so it correctly maps `src/main.py`. If you deploy an empty folder, the API crashes with `500` or `404` which breaks the frontend.
- **Frontend vs Backend Previews**: Vercel's GitHub integration will comment with TWO preview URLs per commit (one for `gudfud-web` and one for `gudfud-api`). If the user clicks the API preview URL, it will hit the backend directly.
- **API Root Redirect**: Because users occasionally click the backend API preview link by mistake (expecting to see the website UI), the `src/main.py` root route (`@app.get("/")`) MUST ALWAYS return an HTTP 307 Redirect (`RedirectResponse(url="https://gudfud-web.vercel.app/")`). This ensures the user is securely bounced to the frontend website and doesn't stare at raw API JSON thinking the site is "broken".

## Code Maintenance
- Ensure `src/main.py` is the single source of truth for FastAPI routing, maintaining the redirect.
- Ensure `IngredientMapping` in `src/schemas.py` and `Ingredient` frontend types remain strictly synchronized.
