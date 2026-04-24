# MavAdvisor - Setup & Run Guide

## Project Structure

```
mavadvisors/
├── backend/        # Flask API server (default port 5001)
├── frontend/       # Flask template server (default port 8080)
├── clear_cache.py  # Clear Python cache
└── README.md       # This file
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs at **http://127.0.0.1:5001**

### 2. Frontend Setup

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Frontend runs at **http://127.0.0.1:8080** (default; override with `FRONTEND_RUN_PORT`)

Visit **http://127.0.0.1:8080** in your browser.

---

## Configuration

### Backend Config (`backend/config.py`)

Environment variables (all optional):

| Variable | Default | Purpose |
|----------|---------|---------|
| `BACKEND_RUN_HOST` | `127.0.0.1` | Backend server host |
| `BACKEND_RUN_PORT` | `5001` | Backend server port |
| `BACKEND_RUN_DEBUG` | `true` | Debug mode |

**Example:**
```bash
BACKEND_RUN_PORT=5001 BACKEND_RUN_DEBUG=true python app.py
```

### Frontend Config (`frontend/config.py`)

Environment variables:

| Variable | Default | Required | Purpose |
|----------|---------|----------|---------|
| `FRONTEND_RUN_HOST` | `0.0.0.0` | No | Frontend server host |
| `FRONTEND_RUN_PORT` | `8080` | No | Frontend server port |
| `FRONTEND_RUN_DEBUG` | `true` | No | Debug mode |
| `BACKEND_HOST` | `127.0.0.1` | No | Backend host (for API calls) |
| `BACKEND_PORT` | `5001` | No | Backend port (for API calls) |
| `BACKEND_API_BASE` | `http://127.0.0.1:5001` | No | Full backend URL (overrides host/port) |
| `OPENAI_API_KEY` | _(empty)_ | **Yes** | OpenAI API key for chatbot |
| `OPENAI_MODEL` | `gpt-4` | No | OpenAI model |

**Create `.env` in `frontend/` folder:**
```
FRONTEND_RUN_PORT=8080
BACKEND_API_BASE=http://127.0.0.1:5001
OPENAI_API_KEY=sk-proj-your-key-here
```

**Example:**
```bash
OPENAI_API_KEY=your-key-here python app.py
```

---

## Database Management

Run database utilities from `backend/`:

```bash
cd backend
python db.py
```

### Available Functions

**`init_db()`** - Initialize/create the SQLite database and users table (runs automatically on server start)

**`clear_all_users_and_files()`** - Delete all users from database AND all user JSON files
- Use when: You want a fresh start
- Deletes: `users.db` entries + `backend/users/*.json` files

**`delete_user(username)`** - Delete a specific user and their JSON file
- Use when: You want to remove one user
- Deletes: User record + `backend/users/{username}.json`

The interactive menu in `db.py` lets you safely choose operations with confirmations.

---

## Clear Python Cache

Remove all `__pycache__` and `.pyc` files:

```bash
python clear_cache.py
```

Run from project root before committing.

---

## File Structure

- **`backend/app.py`** - Main API server
- **`backend/config.py`** - Backend configuration
- **`backend/db.py`** - Database & user management
- **`frontend/app.py`** - Frontend template server
- **`frontend/config.py`** - Frontend configuration
- **`frontend/templates/`** - HTML pages
- **`frontend/static/`** - CSS, JS, images

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change `FRONTEND_RUN_PORT` or `BACKEND_RUN_PORT` |
| Can't connect to backend | Check `BACKEND_API_BASE` in frontend config |
| Chatbot not working | Set `OPENAI_API_KEY` environment variable |
| Database errors | Run `python db.py` and clear all users, then restart |

---

## Running Both (Recommended Setup)

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
OPENAI_API_KEY=your-key python app.py
```

Then open browser to **http://127.0.0.1:8080**
