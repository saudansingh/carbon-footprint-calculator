# Carbon Footprint Calculator & Tracker with AI-Powered Recommendations

## 1) Architecture Overview
- **Frontend (React + Vite)**: SPA with routes for Dashboard, Activities, Recommendations, Profile. Uses Chart.js via react-chartjs-2.
- **Backend (Flask)**: REST API with JWT auth, activity CRUD, analytics (summary/trend/comparison), AI recommendation endpoint.
- **Database (MongoDB)**: Collections `users`, `activities`, `ai_usage`.
- **AI Integration (OpenAI)**: API-based recommendation generation with safe fallback heuristics and basic rate-limiting.

Data flow: React calls Flask `/api/*` endpoints with JWT. Activities are inserted with computed `emission_kg`. Analytics aggregate by date/category. Recommendations read recent data and call OpenAI (or fallback) to suggest actions.

## 2) Folder Structure
```
planet_sustech_prj1/
  backend/
    app/
      __init__.py
      config.py
      db.py
      routes/
        auth_routes.py
        activity_routes.py
        analytics_routes.py
        recommendation_routes.py
      utils/
        emissions.py
        ai.py
    scripts/
      seed_sample.py
    server.py
    requirements.txt
    .env.example
  frontend/
    index.html
    vite.config.js
    package.json
    .env.example
    src/
      main.jsx
      App.jsx
      styles.css
      api.js
      state/
        AuthContext.jsx
      pages/
        Login.jsx
        Register.jsx
        Dashboard.jsx
        Activities.jsx
        Recommendations.jsx
        Profile.jsx
  README.md
  AI_USAGE_REPORT.md
```

## 3) Backend Endpoints
- `POST /api/auth/register` email,password,name -> JWT + user
- `POST /api/auth/login` -> JWT + user
- `GET /api/auth/me` -> user
- `PUT /api/auth/me` name/password -> updated user
- `POST /api/activities` {date,type,data} -> create
- `GET /api/activities?start=YYYY-MM-DD&end=YYYY-MM-DD&limit=50` -> list
- `PUT /api/activities/:id` -> update (recomputes emissions on type/data change)
- `DELETE /api/activities/:id` -> delete
- `GET /api/analytics/summary?start&end` -> totals + by_category
- `GET /api/analytics/trend?start&end` -> per-day totals
- `GET /api/analytics/comparison?period=week|month` -> compare with previous
- `GET /api/recommendations?days=30` -> AI suggestions with summary and recent

Activity `type` values and formulas:
- car: distance_km × 0.12
- flight: distance_km × 0.255
- electricity: kWh × 0.5
- beef_meal: 6.0 kg/meal
- vegetarian_meal: 1.5 kg/meal
(+ optional: bus 0.089×km, train 0.041×km)

## 4) Local Setup
### Prereqs
- Node 18+
- Python 3.10+
- MongoDB running locally at `mongodb://localhost:27017`
- (Optional) OpenAI API key

### Backend
```
cd planet_sustech_prj1/backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # fill OPENAI_API_KEY to enable AI model
python server.py
```
Server runs at http://localhost:5000

Seed sample data (optional):
```
python scripts/seed_sample.py
```

### Frontend
```
cd planet_sustech_prj1/frontend
npm install
copy .env.example .env  # ensure VITE_API_URL points to backend
npm run dev
```
Open http://localhost:5173

## 5) Example API Responses
- Register/Login:
```
{
  "token": "<jwt>",
  "user": {"id": "...", "email": "demo@example.com", "name": "Demo"}
}
```
- Create Activity:
```
{
  "id": "...",
  "user_id": "...",
  "date": "2026-01-31",
  "type": "car",
  "category": "transport",
  "data": {"distance_km": 12},
  "emission_kg": 1.44,
  "created_at": "...",
  "updated_at": "..."
}
```
- Analytics Summary:
```
{
  "total_kg": 42.1,
  "by_category": {"transport": 21.5, "energy": 15.2, "food": 5.4}
}
```
- Recommendations:
```
{
  "window_days": 30,
  "summary": { ... },
  "source": "openai|heuristic|fallback|rate_limit",
  "items": [{"category": "transport", "advice": "Use public transit twice a week."}]
}
```

## 6) Screenshots to Capture (for demo)
- Login page
- Dashboard showing line chart and pie breakdown
- Activities page with add/edit/delete and list
- Recommendations panel with badges and advice items
- Profile update

## 7) Security & Production Notes
- JWT secret must be strong and rotated for production; use HTTPS in deployment.
- CORS restricted via `CORS_ORIGINS` env; set to your frontend URL(s).
- Never commit real API keys. Use environment variables.
- Use Gunicorn/Waitress for server in production and set `debug=False`.

## 8) AI Prompt Logic (summary)
- System prompt: sustainability coach persona, require JSON `{ items:[{category,advice}] }` output.
- User content: profile summary + category totals + 50 most recent activities.
- Temperature 0.4; hard filters categories; rate-limit with `AI_RATE_LIMIT_SECONDS`.
- Fallback to deterministic heuristics if API missing or fails.

## 9) Submission Checklist
- [x] Complete backend (auth, CRUD, analytics, AI)
- [x] Complete frontend (auth, dashboard, activities, recs, profile)
- [x] MongoDB schemas and indexes
- [x] Env files and requirements
- [x] Sample data + example responses
- [x] README with run instructions
- [x] AI Usage Report
