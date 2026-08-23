<<<<<<< HEAD
# DineMapAI
=======
# DineMapAI — Backend (Flask)

Serves the three endpoints the frontend already calls from `js/api.js`.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

The server runs at `http://127.0.0.1:5000` — this already matches `API_BASE_URL` in the frontend's `js/api.js`.

## Connect it to the frontend

In `js/api.js`, set:

```js
const USE_MOCK_DATA = false;
```

That's it — every page will now call this server instead of using fake data.

## Files

| File | What it does |
|---|---|
| `app.py` | The Flask app — all three routes live here |
| `mock_data.py` | Sample dashboard data + a demo user list for `/login` |
| `requirements.txt` | Just Flask — no extra packages needed |

## Endpoints

| Method | Endpoint | Body (JSON) | Returns |
|---|---|---|---|
| GET | `/` | — | Health check |
| POST | `/login` | `{ username, password }` | `{ success, message }` |
| GET | `/dashboard-data` | — | Full dashboard dataset |
| POST | `/analyze-location` | `{ cityArea, restaurantType, targetAudience, budgetRange, businessGoals, additionalPreferences, timingSlots }` | `{ success, message }` |

## Demo login credentials

These are hardcoded in `mock_data.py` for testing only — **replace with a real database and hashed passwords before deploying**:

- `demo` / `demo123`
- `admin` / `admin123`

## Adding a new endpoint

1. Add a new function in `app.py` with an `@app.route(...)` decorator.
2. Add a matching function in the frontend's `js/api.js` using `postData()` or `fetchData()`.

## CORS

`app.py` includes a small `after_request` handler that adds CORS headers manually (no extra package required), since the frontend may be opened as a plain HTML file or served from a different port. Before deploying, replace the `"*"` origin with your actual frontend URL.
>>>>>>> 8f7e47c (Updated Backend with Multiple fallback urls. To try if one fails after the other.)
