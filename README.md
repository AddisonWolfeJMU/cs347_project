# cs347_project

This repo contains a Django backend and a Svelte (Vite) frontend.

## Frontend (Svelte + Vite)

### Run Dev Server
```powershell
cd frontend
npm install
npm run dev
```
Open the URL shown in the terminal (localhost)

### Edit UI
- `frontend\src\App.svelte` — main app
- `frontend\src\app.css` — global styles
- `frontend\src\pages` - all pages

## Backend (Django)

From the root:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Backend will serve at http://127.0.0.1:8000.


