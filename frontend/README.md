# SmartSched AI Frontend

Frontend starter for the SmartSched AI hackathon project.

## Stack
- React + Vite
- Tailwind CSS
- React Router
- Lucide React
- Recharts

## Run
```bash
npm install
npm run dev
```

Open the local URL shown by Vite.

## Demo flow
1. Login with any non-empty email/password.
2. Open Production Schedule.
3. Click Simulate Disruption.
4. Select Machine Failure -> M2 -> 120 minutes.
5. Apply the disruption.
6. Watch M2 become FAULT and the revised schedule appear.

The frontend currently uses mock data. FastAPI + OR-Tools can be connected later through `src/services/api.js`.
