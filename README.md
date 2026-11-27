# CyberShield – Cyber Fraud Detection System

React + Vite frontend, Flask API, SQLite database. Checks links and messages with transparent, rule-based
indicators. It never opens the links it checks and never claims a result is proof.

## Run on Windows (two terminals)

**Terminal 1 – backend**
```
cd CyberShield\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python test_api.py
python app.py
```
Check http://127.0.0.1:5000/api/health in your browser. It should show `{"status":"ok"}`.

**Terminal 2 – frontend**
```
cd CyberShield\frontend
npm install
copy .env.example .env
npm run dev
```
Open http://localhost:5173

## Test the API from PowerShell
```
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/scan -ContentType "application/json" -Body '{"type":"url","input":"http://192.168.1.5/verify-account"}'
Invoke-RestMethod http://127.0.0.1:5000/api/stats
Invoke-RestMethod "http://127.0.0.1:5000/api/history?risk=High"
```

## API
| Method | Path | Purpose |
|---|---|---|
| POST | /api/scan | `{type: "url"\|"text", input}` → analyze and save |
| GET | /api/history | `search`, `risk`, `type`, `page`, `per_page` |
| DELETE | /api/history/<id> | delete one record |
| DELETE | /api/history | delete all |
| GET | /api/stats | dashboard numbers |
| GET | /api/health | status |

## Common problems
- **"Can't reach the server"**: backend isn't running, or `VITE_API_URL` is wrong. Restart `npm run dev` after editing `.env`.
- **CORS error in browser console**: add your frontend address to `CORS_ORIGINS` in `backend\.env`, then restart Flask.
- **`python` not found**: install Python 3.10+ and tick "Add to PATH". Try `py` instead of `python`.
- **PowerShell blocks `activate`**: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use Command Prompt.

## Deployment notes (details come in Phase 7)
- Frontend: Vercel or Netlify. Set `VITE_API_URL=https://YOUR-BACKEND/api`.
- Backend: Render web service (`gunicorn app:app`) with a **persistent disk** mounted at `/var/data`, and
  `DATABASE_PATH=/var/data/cybershield.db`. Free Render instances have no persistent disk, so SQLite data would be lost.
- Set `CORS_ORIGINS` to your exact frontend URL.
