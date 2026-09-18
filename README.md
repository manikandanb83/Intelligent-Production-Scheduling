# SmartSched-AI

Adaptive production scheduling for a small factory: a FastAPI backend that runs an
OR-Tools CP-SAT scheduler over a simulated factory floor (machines, orders,
disruptions), paired with a React + Vite frontend.

## Project Structure

```
SmartSched-AI/
│
├── README.md
│
├── docs/
│   ├── architecture.png              # pending
│   ├── problem-statement-alignment.md
│   └── development-history.md
│
├── backend/
│   ├── main.py                       # FastAPI app & routes
│   ├── models.py                     # Pydantic request/response models
│   ├── optimizer_client.py           # HTTP client for an external optimizer service
│   │
│   ├── optimizer/
│   │   ├── __init__.py
│   │   └── scheduler.py              # CP-SAT scheduling logic
│   │
│   └── simulation/
│       ├── __init__.py
│       └── factory.py                # Virtual factory state (machines, downtime)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── services/api.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── .gitignore
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install fastapi uvicorn pydantic ortools httpx
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- `docs/` currently holds placeholders — drop in `architecture.png` and fill out the
  two markdown files when you upload the rest of your documentation.
- No dataset archive came through with this upload (only backend + frontend zips) —
  add a `dataset/` folder once you have that file.

## Known Issues to Fix Before Running

- `backend/main.py` uses `BaseModel` (for `MachineFailure`) but only imports `FastAPI`
  — add `from pydantic import BaseModel`.
- `backend/optimizer/scheduler.py` stops partway through `optimize_schedule()`, right
  after computing `MAX_TIME` — it never builds the CP-SAT variables, solves the model,
  or returns a result. It needs the rest of the optimization logic (variables,
  constraints, objective, solve, and the schedule/KPI dict it returns) before the
  `/reoptimize` endpoint will work.
- `backend/simulation/__init__.py` and `backend/simulation/factory.py` currently
  duplicate the same factory-state logic — worth trimming `__init__.py` down to just
  `from .factory import *` once you're ready to clean it up.
