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

## 💻 Setup and Scripts

### Environment Variables
Set up your backend `.env` based on `.env.example`. Make sure `DATABASE_URL` points to your PostgreSQL instance (e.g., your local Supabase or cloud URL). 
For the frontend, configure `apps/web/.env` and `apps/web/.env.production` where `NEXT_PUBLIC_API_URL` points to the FastAPI server.

### Running the Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Running the Frontend
```bash
cd apps/web
npm install
npm run dev
```

### Database Migrations
Modifications to the schema require running Alembic migrations:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### ML Scoring Population
To re-evaluate products and update scores in bulk, use the scoring scripts (e.g., `update_scores3.py`) which recalculate nutrition, ingredient, and total scores and apply them directly to the database.
```bash
python update_scores3.py
```
