# Copilot instructions — Contact Manager (student project)

Purpose: Help AI coding agents be immediately productive in this repository.

- **Big picture:** Single-process Flask app in `app.py` that serves `templates/index.html`. Data is stored in-memory in the `contacts` list and persisted to `contacts.json` via `load_contacts()` / `save_contacts()`.
- **Run locally:** `python app.py` (app listens on port 5000; `debug=True` is enabled in `app.py`). Install deps with `pip install -r requirements.txt`.
- **Containers:** `Dockerfile` builds a Python image (includes MS ODBC setup). Use `docker-compose up --build` to bring up the app plus `postgres_db` and `mssql_db` services described in `docker-compose.yml` (note: the compose file mounts the repo into `/app`).

- **Key files to inspect when changing behavior:**
  - `app.py` — routes and the in-memory `contacts` logic (search, add, persistence).
  - `templates/index.html` — expected template variables: `contacts`, `title`, `search_performed`, `search_query`.
  - `contacts.json` — persisted contacts; `CONTACTS_FILE` constant in `app.py` points here.
  - `requirements.txt`, `Dockerfile`, `docker-compose.yml` — containerization and DB driver setup.

- **Project-specific patterns / conventions:**
  - Phase-based comments: `app.py` contains clearly-labeled Phase 1 / later-phase placeholders. Agents should follow these markers when adding data-structure or DB code (e.g., replace list operations inside the Phase 1 area rather than scattering changes across unrelated functions).
  - Persistence is file-based by default: keep `save_contacts()` calls (or replace with equivalent persistence when switching to a DB) so front-end behavior stays consistent.
  - Route contract: `/` (GET) renders `index.html`; `/add` (POST) expects `name` and `email`; `/search` (POST) expects `search_query` and renders search results via the same template.

- **When adding DB integration:**
  - `app.py` contains `get_postgres_connection()` and `get_mssql_connection()` placeholders. Use these single-entry helpers to centralize connection logic and environment-variable use.
  - `docker-compose.yml` exposes default credentials (student/password123/Password123!) — use these values for local development only.

- **Concrete examples & snippets to follow**
  - To append a contact (current pattern):

    contacts.append({'name': name, 'email': email})
    save_contacts()

  - To render search results: return `render_template('index.html', contacts=search_results, search_performed=True, search_query=search_query)`

- **Common tasks & commands**
  - Install deps: `pip install -r requirements.txt`
  - Run locally: `python app.py`
  - Docker compose: `docker-compose up --build` (mounts code; restart the service to pick up major changes in Docker context)

- **Safety & scope:** Only modify the Phase 1 region when implementing student assignments unless explicitly expanding to DB integration. Preserve template variable names and `save_contacts()`/`load_contacts()` semantics so the UI continues to work.

If anything above is unclear or you want additional, narrower examples (e.g., converting the in-memory list to a linked list or wiring Postgres), tell me which area to expand.
