# Frontend

This frontend targets the backend API on `main` at commit `e927ccc`.
Backend code matches this main revision. The root `docker-compose.yaml` also
includes the frontend service so the application can be started with one file.

Start the main backend separately using its README, then run from this directory:

```powershell
npm ci
npm run dev
```

Open http://localhost:5173. The default `/api` base uses the Vite proxy to
http://localhost:8000; `/media` is also proxied. An existing frontend `.env` can
override this with `VITE_API_URL=http://localhost:8000`. Use the same hostname
for browser and API so session cookies work. The main backend allows port 5173
by default. For a frontend Nginx deployment, allow that site's origin in the
backend deployment configuration.

Integration behavior:

- Login sends email, password and remember_me; session cookies are sent with
  requests. The profile is fetched after login because login returns only username.
- Profile updates use PATCH /users/me with city, discipline, interests and bio.
  Interests are entered as comma-separated values and sent as a list.
- Feed pagination uses items/next_cursor. Search and category filters apply to
  loaded posts locally because the backend has no search/category parameters.
- Creating a post sends title, text and an English category identifier. Optional
  JPEG/PNG photos are uploaded separately to PUT /posts/{id}/photo. If photo
  upload fails, retry reuses the saved post instead of creating a duplicate.
- Bikes use /users/me/bikes. Username editing, avatar uploads, bike photos and
  rich text controls are omitted because main does not expose those operations.
- The former author-filtered profile feed is omitted because main has no
  author_id filter; the public feed remains available.

Validation:

```powershell
npm run build
# From the repository root, install frontend browser-check dependencies:
.venv/Scripts/python.exe -m pip install -r frontend/tests/requirements.txt
.venv/Scripts/python.exe frontend/tests/verify_main_contract.py
```

The browser check runs the built frontend at 1440px and 390px with mocked API
responses matching main, including cursor pagination, registration, auth errors,
profile edits, bike creation, text/photo posts and failed photo upload retries.
It does not connect to a backend or change a database. Live integration with the
main backend remains a separate check.

To run the frontend container alongside the backend, run from the repository root:

```powershell
docker compose up -d --build
```

Configure the root `.env` according to main's `.env.example` first. Run the
database migrations as described in the root README. The frontend is available
at http://localhost:5173 and proxies API and media requests to the backend.
