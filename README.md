# Document Summary Assistant

This repository is a starter scaffold for a document summarization assistant application (upload → extract → summarize → display).

Tech stack (recommended):

- Backend: Flask
- PDF extraction: pdfminer.six
- OCR: Tesseract + pytesseract
- Summarization: OpenAI or HuggingFace (optional)
- Frontend: simple static UI (can be replaced by React)

What I added

- `backend/` — Flask app and helper modules (extraction + summarization stubs)
- `frontend/` — simple static page to try the endpoints
- `.env.example` — example environment variables
- `LICENSE`, `.gitignore`, and a top-level `README.md`

## Features (MVP)

- Upload PDF or image for text extraction
- View & edit extracted text
- Generate summary (Short / Medium / Long)
- React UI with clean layout and basic states

Planned enhancements: key bullet points, improvement suggestions, dark mode, copy-to-clipboard, section-wise summary.

Quick start (backend only):

1. Create and activate a Python virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Run the backend

```bash
# Option A: Run as a Flask app using the package path
FLASK_APP=backend.app FLASK_ENV=development flask run

# Option B: Run directly with Python
python -m backend.app
```

3. (Optional) If you build the React frontend (see below), Flask will serve it from `frontend/dist/`.

## React Frontend (Vite)

Dev server setup:

```bash
cd frontend
npm install
npm run dev
```

This starts Vite on `http://localhost:5173`. API calls hit the Flask backend at `http://127.0.0.1:5000` (adjust `VITE_API_BASE_URL` in a `.env` file inside `frontend/` if needed).

Build production assets:

```bash
npm run build
```

Output goes to `frontend/dist/`. Restart Flask so it serves the built UI at `/`.

### Frontend Features (initial)

- Upload PDF/Image → extraction via `/api/upload`
- Choose summary length (Short/Medium/Long) → `/api/summarize`
- Display summary text

### Next Enhancements

- Key bullet points & suggestions (extend summarizer)
- Loading states & error banners
- Dark/light toggle & clipboard copy button
- Section-wise summary & download as .txt

Notes

- The summarizer currently uses a simple heuristic (first N sentences). Replace with OpenAI/HuggingFace calls in `backend/summarize.py` when ready.
- CORS is enabled for `/api/*` endpoints to allow the React dev server to communicate with Flask.
