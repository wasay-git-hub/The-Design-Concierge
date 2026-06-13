# The Design Concierge — Agentic Discovery System

The Design Concierge is an automated **Digital Junior Designer** for high-end boutique interior design firms (targeting luxury markets in Miami, Austin, and Scottsdale). It transforms the typical 2–4 hour manual client onboarding and discovery leak into a 5-minute pre-qualified briefing.

---

## Core System Features

1. **Visual Empathy (GPT-4o Vision API)**: Analyzes client-uploaded room photos, extracting architectural bones, natural light orientation, existing style, and dimensions to ensure the client feels understood instantly.
2. **Taste & Style DNA Discovery (Stateful LangGraph)**: Orchestrates a refined, professional chat interview that identifies mismatches between user requests (e.g., "Airy Scandinavian") and spatial limitations (e.g., a dark basement), presenting custom designer workarounds.
3. **Project Readiness Scoring**: Aggregates timeline, scope, and visual constraint alignment to calculate a lead readiness score (0-100) so designers can prioritize high-value client bookings.
4. **PDF Intelligence Report (ReportLab)**: Generates a luxury-branded, technical project briefing PDF for the architect/designer's 1-on-1 consultation.
5. **LLM Observability (Langfuse)**: Natively tracks token usage, API latency, and conversation traces for the backend agent across all sessions.

---

## Project Directory Structure

```
c:\Users\wasay\The-Design-Concierge\
├── src/
│   ├── frontend/                 # Next.js App
│   │   ├── src/app/
│   │   │   ├── page.tsx          # Client onboarding interface
│   │   │   └── designer/page.tsx # Designer lead management dashboard
│   │   ├── package.json          # Next.js dependencies
│   │   └── tailwind.config.ts    # Custom branding tokens
│   │
│   └── backend/                  # Python FastAPI Service
│       ├── api_app.py            # FastAPI routers & endpoints
│       ├── database.py           # SQLAlchemy SQLite models
│       ├── config.py             # System paths and variables
│       ├── graphs/
│       │   ├── workflow.py       # LangGraph routing compilation
│       │   └── nodes.py          # Onboarding, Vision & Refinement logic
│       └── utils/
│           └── pdf_generator.py  # ReportLab luxury PDF layout compiler
├── data/                         # Local SQLite databases (database.sqlite, checkpoints.sqlite)
├── static/                       # Uploaded room photos and generated PDFs
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable templates
└── README.md                     # Documentation
```

---

## Quick Start Guide

### 1. Backend Service Setup & Start
Navigate to the root directory `c:\Users\wasay\The-Design-Concierge`.

#### A. Configure Environment
1. In the root folder, duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and insert your OpenAI API Key:
   ```env
   OPENAI_API_KEY=sk-...

   # (Optional) Langfuse Analytics Keys
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=your_langfuse_base_url
   ```
   *Note: If no OpenAI key is specified, the application will run in fallback simulation mode so you can fully test the flow without API charges.*

#### B. Start the FastAPI Server
Launch the API server on `http://localhost:8000`:
```bash
python -m uvicorn src.backend.api_app:app --reload
```

---

### 2. Frontend Application Setup & Start
*Note: Make sure Node.js is installed on your computer.*

#### A. Install Next.js Dependencies
Navigate to the `src/frontend` directory:
```bash
cd src/frontend
npm install
```

#### B. Start Next.js Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your web browser to start the Client Onboarding flow. Go to `http://localhost:3000/designer` to inspect the Designer Dashboard.