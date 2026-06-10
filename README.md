# The Design Concierge — Agentic Discovery System

The Design Concierge is an automated **Digital Junior Designer** for high-end boutique interior design firms (targeting luxury markets in Miami, Austin, and Scottsdale). It transforms the typical 2–4 hour manual client onboarding and discovery leak into a 5-minute pre-qualified briefing.

---

## Core System Features

1. **Visual Empathy (GPT-4o Vision API)**: Analyzes client-uploaded room photos, extracting architectural bones, natural light orientation, existing style, and dimensions to ensure the client feels understood instantly.
2. **Taste & Style DNA Discovery (Stateful LangGraph)**: Orchestrates a refined, professional chat interview that identifies mismatches between user requests (e.g., "Airy Scandinavian") and spatial limitations (e.g., a dark basement), presenting custom designer workarounds.
3. **ML-Driven Budget Estimator (`GradientBoostingRegressor`)**: Predicts project cost ranges using a Gradient Boosting model trained on high-end renovation indexes. The assistant presents the estimate without negotiating, leaving customization to the designer.
4. **Project Readiness Scoring**: Aggregates timeline, decision-maker status, scope, and budget alignment to calculate a lead readiness score (0-100) so designers can prioritize high-value client bookings.
5. **PDF Intelligence Report (ReportLab)**: Generates a luxury-branded, technical project briefing PDF for the architect/designer's 1-on-1 consultation.

---

## Project Directory Structure

```
c:\Users\wasay\The-Design-Concierge\
├── frontend/                     # Next.js App
│   ├── src/app/
│   │   ├── page.tsx              # Client onboarding interface
│   │   └── designer/page.tsx     # Designer lead management dashboard
│   ├── src/app/globals.css       # Tailwind rules & scrollbars
│   ├── package.json              # Next.js dependencies
│   └── tailwind.config.js        # Custom branding tokens
│
├── backend/                      # Python FastAPI Service
│   ├── app/
│   │   ├── main.py               # FastAPI routers & endpoints
│   │   ├── db.py                 # SQLAlchemy SQLite models
│   │   ├── config.py             # System paths and variables
│   │   ├── graphs/
│   │   │   ├── workflow.py       # LangGraph routing compilation
│   │   │   └── nodes.py          # Onboarding, Vision & Refinement logic
│   │   ├── ml/
│   │   │   └── model.py          # Cost prediction inference module
│   │   └── utils/
│   │       └── pdf_generator.py  # ReportLab luxury PDF layout compiler
│   ├── train_budget_model.py     # Gradient Boosting model training script
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Environment variable templates
└── README.md                     # Documentation
```

---

## Quick Start Guide

### 1. Backend Service Setup & Start
Navigate to the root directory `c:\Users\wasay\The-Design-Concierge`.

#### A. Configure Environment
1. In the `backend` folder, duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Open `backend/.env` and insert your OpenAI API Key:
   ```env
   OPENAI_API_KEY=sk-...
   ```
   *Note: If no API key is specified, the application will run in fallback simulation mode so you can fully test the flow without API charges.*

#### B. Train the ML Cost Model
Before launching the backend, you must train and serialize the Gradient Boosting model.
1. Place your Kaggle or custom project estimation CSV dataset as `budget_data.csv` in the root folder.
   *Note: If `budget_data.csv` is not found, the script will automatically generate a highly realistic dataset based on luxury industry renovation cost statistics for Miami, Austin, and Scottsdale to run out-of-the-box.*
2. Train the model:
   ```bash
   venv\Scripts\python backend/train_budget_model.py
   ```
3. Once completed, you will see the model's metrics (R-squared score and Mean Absolute Error) and the serialized pipeline saved to `backend/app/ml/budget_model.joblib`.

#### C. Start the FastAPI Server
Launch the API server on `http://localhost:8000`:
```bash
venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

---

### 2. Frontend Application Setup & Start
*Note: Make sure Node.js is installed on your computer.*

#### A. Install Next.js Dependencies
Navigate to the `frontend` directory:
```bash
cd frontend
npm install
```

#### B. Start Next.js Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your web browser to start the Client Onboarding flow. Go to `http://localhost:3000/designer` to inspect the Designer Dashboard.