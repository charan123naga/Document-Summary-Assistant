# Backend

Contains a minimal Flask app and helper modules for extraction and summarization.

Run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
FLASK_APP=backend/app.py flask run
```
 
## Summarization (Day 3)

Endpoint: `POST /api/summarize`

Request JSON:

```json
{ "text": "<extracted text>", "level": "short|medium|long" }
```

Response JSON (heuristic implementation; future upgrade will swap in LLM):

```json
{
	"summary": "First N sentences heuristic summary",
	"points": ["Key sentence 1", "Key sentence 2"],
	"suggestions": ["Passive constructions detected; active voice may improve engagement."],
	"level": "short",
	"chars": 1234
}
```

Field meanings:
 - `summary`: Concise overview (length depends on level)
 - `points`: Most content-rich sentences in original order
 - `suggestions`: Simple writing quality heuristics
 - `chars`: Original text character length (post normalization)

You can safely expand the summarization logic by replacing `backend/summarize.py:summarize()` with an LLM call that still returns the same shape. Keep tests passing by preserving keys.
