# Backend (FastAPI + LangGraph)

Quickstart:

1. Create venv and install deps

   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate  # Windows
   pip install -r backend/requirements.txt
   ```

2. Run the server

   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

3. Frontend env

   Add to `.env`:

   ```
   VITE_BACKEND_URL=http://127.0.0.1:8000
   ```

Endpoints:
- POST /api/chat { message, conversationId?, history? }
- GET /api/reports/{id} -> PDF

This backend uses LangGraph to orchestrate simple mock agents and returns a summary + optional PDF report id.
