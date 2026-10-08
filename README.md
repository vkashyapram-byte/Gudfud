# GudFud - Transparent Food Label Analysis

GudFud is an independent AI platform that deeply analyzes packaged food products based on a rigorous 100-point scale. It features a Python FastAPI backend for Machine Learning ingestion/scoring, a PostgreSQL database (Supabase) managed via SQLAlchemy/Alembic, and a highly responsive Next.js frontend deployed on Vercel.

---

## 🎯 Project Philosophy & Architecture

GudFud aims to prioritize education and food transparency over commerce. The architecture is a modern monorepo separating the intensive ML calculations from the user interface:

- **Frontend (`apps/web/`)**: A Next.js application designed with a sleek, minimalist, monochrome UI. The design is strictly health-focused and actively avoids typical ecommerce patterns, prioritizing readability and nutritional clarity.
- **Backend (Root `src/`)**: A Python FastAPI server that serves the database API and handles the ML-driven evaluation of products. It connects to a Supabase PostgreSQL instance.
- **Database**: Managed via Alembic migrations, utilizing models for `Product`, `ProductVariant`, `LabelVersion`, `Rating`, `Ingredient`, and `NutritionFacts`.

---

## 🧠 The Scoring Engine

At the core of GudFud is the scoring engine, which automatically evaluates packaged foods. The final score is out of **100 points** and is derived from a weighted heuristic:

1. **Nutrition (50% Weight)**: Evaluates the macroscopic health data of the product, specifically penalizing high levels of sugars, saturated fat, and sodium against recommended health limits.
2. **Ingredients (30% Weight)**: Analyzes the raw ingredients list. Longer, highly-processed ingredient lists are penalized. It rigorously searches for harmful additives, artificial preservatives, and synthetic colors, generating comprehensive "Harmful Ingredients" alerts.
3. **Context (20% Weight)**: Evaluates contextual modifiers such as processing level (e.g., NOVA classification).

### Scoring Bands
Based on the final 100-point score, the engine computes a safety band:
- **Mostly favourable (Score 70 - 100)**: Excellent choice, minimal harmful additives, highly nutritious.
- **Moderate (Score 40 - 69)**: Moderate choice, likely some processing or elevated sugars/sodium.
- **Mostly unfavourable (Score 0 - 39)**: Poor choice, highly processed or severely unhealthy.

This rating, alongside the final `X/100` score, is clearly surfaced on the catalogue cards and the individual product pages.

---

## 🔬 "Good & Bad" Analysis 

GudFud goes beyond simple scoring by actively generating easy-to-understand nutritional and ingredient summaries directly on the product detail pages.

Rather than forcing users to navigate to separate pages to understand complex chemical additives, GudFud integrates **"About this Item"** sections under the Nutrition facts. These sections explicitly highlight what is good or bad about the specific item, exposing harmful ingredients natively and providing context for the product's final score without overwhelming the user.

---

## 💻 Setup and Scripts (Extensively Detailed)

### 1. Prerequisites
Before getting started, ensure you have the following installed on your system:
- **Python 3.10+**: For running the FastAPI backend and ML scripts.
- **Node.js (v18+) & npm**: For running the Next.js frontend.
- **Supabase CLI**: For local database management and querying the linked production PostgreSQL instance.
- **Vercel CLI**: For deploying the separate API and Frontend projects.

### 2. Environment Variables Configuration
You must configure environment variables for both the backend and frontend separately.

**Backend (Root Directory)**
Create a `.env` file at the root of the project:
```env
DATABASE_URL="postgresql://postgres:postgrespassword@localhost:5432/gudfud" # Example local Supabase URL
```

**Frontend (`apps/web/`)**
Create an `.env.local` (and optionally `.env.production` for production builds) inside `apps/web/`:
```env
NEXT_PUBLIC_API_URL="http://localhost:8000" # Development API URL
# Or for production:
# NEXT_PUBLIC_API_URL="https://gudfud-api.vercel.app"
```

### 3. Database Initialization (Supabase & Alembic)
The project uses PostgreSQL, managed via Supabase, with schemas defined by SQLAlchemy and migrated using Alembic.

1. Initialize and start your local Supabase instance (or link to a cloud instance):
   ```bash
   supabase init
   supabase start
   ```
2. Apply the database migrations to generate the schema:
   ```bash
   alembic upgrade head
   ```

### 4. Running the Local Development Environment
The monorepo requires running two separate development servers simultaneously.

**Terminal A: Start the Python FastAPI Backend**
```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Uvicorn server (Accessible at http://localhost:8000)
uvicorn src.main:app --reload --port 8000
```

**Terminal B: Start the Next.js Frontend**
```bash
# 1. Navigate to the web app directory
cd apps/web

# 2. Install Node dependencies
npm install

# 3. Start the Next.js development server (Accessible at http://localhost:3000)
npm run dev
```

### 5. Data Ingestion & ML Scoring Pipeline
To populate the database with product data and generate the ML-based scores, utilize the provided data pipeline scripts.

1. **Populate Base Data**: Run the population scripts to ingest ingredient catalogs and safe limits.
   ```bash
   python scripts/populate_safe_limits.py
   python populate_supa.py
   ```
2. **Calculate and Update Scores**: Execute the scoring script to compute the `total_score`, `nutrition_score`, and `ingredient_score` based on the 100-point heuristic model.
   ```bash
   python update_scores3.py
   ```
   *(Note: The `update_scores3.py` script leverages SQLAlchemy to fetch raw `label_version` data, processes the NLP/nutritional rules, and applies an `UPDATE` operation directly back to the database).*

### 6. Deployment Workflow (Vercel)
This monorepo utilizes Vercel for both the frontend and the serverless python backend. They are deployed as two separate Vercel projects:

- **Frontend Deployment**: Deploys the `apps/web/` directory. Vercel automatically detects Next.js.
- **Backend Deployment**: Uses the `vercel.json` and `api/index.py` at the repository root to deploy the FastAPI server via Serverless Functions.

To deploy manually via CLI:
```bash
# Deploy the API
vercel --prod

# Deploy the Web App
cd apps/web
vercel --prod
```
