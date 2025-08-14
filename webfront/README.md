# Web frontend project for Site Analyzer

## Background

This frontend powers the Site Analyzer app. It includes a public marketing page and an authenticated dashboard for managing maps and tasks.

- Stack: React + TypeScript + Vite, Material UI (MUI), TanStack Router (routing), TanStack Query (server state), Google OAuth (auth), and an auto-generated OpenAPI client.
- Structure (key folders):
  - `src/main.tsx`: App bootstrap, GoogleOAuthProvider, QueryClient, global API error handling.
  - `src/App.tsx`: Route tree with protected routes using TanStack Router.
  - `src/marketing-page/`: Landing page and sections (Hero, Features, FAQ, etc.).
  - `src/crud-dashboard/`: Dashboard layout (header/sidebar) and pages: `welcome`, `my-maps`, `new-map`, `users`, `tasks`.
  - `src/shared-theme/`: Central MUI theme (`AppTheme`) and component customizations; supports light/dark mode.
  - `src/sign-in/`, `src/sign-up/`: Auth screens; Sign-In supports Google OAuth code flow and username/password.
  - `src/client/`: Generated API SDK via `@hey-api/openapi-ts` (config: `openapi-ts.config.ts`; source spec: `openapi.json`).

Routing and auth
- Public routes: `/` (marketing), `/sign-in`, `/sign-up`.
- Protected: `/dashboard` and its children. Access requires `access_token` in `localStorage`; missing/expired tokens redirect to `/sign-in`.
- Admin-only examples: `/dashboard/users`, `/dashboard/tasks` (guarded by `isAdmin()`).

API client and data fetching
- `OpenAPI.BASE` is set from `VITE_API_URL`; `OpenAPI.TOKEN` reads `access_token` from `localStorage`.
- Global `ApiError` handling clears the token on 401/403 and redirects to sign-in.
- TanStack Query is used for caching and request lifecycle.

Environment variables
- `VITE_API_URL` (e.g., `http://localhost:8000`) points the SDK to the backend.
- `VITE_GOOGLE_CLIENT_ID` is required for Google Sign-In (see section below).

## Google Sign-In configuration (required)

This frontend uses Google Sign-In. Configure the client ID via Vite env files (which are git-ignored):

- Development: create `./webfront/.env.development`

```
VITE_GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

- Production: create `./webfront/.env.production` with the production client ID.

Notes:
- Only variables prefixed with `VITE_` are exposed to the client at build time.
- Do not commit secrets. Client IDs are public identifiers but still keep env files out of version control.
