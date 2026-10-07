# GudFud - Transparent Food Label Analysis

GudFud is an independent AI platform that deeply analyzes packaged food products based on a rigorous 100-point scale. It features a Python FastAPI backend for Machine Learning ingestion/scoring, a PostgreSQL database managed via SQLAlchemy/Alembic, and a highly responsive Next.js frontend.

---

## The ML Scoring Engine 🧠

At the core of GudFud is our ML Scoring Engine (`src/scorer/engine.py`), built to automatically and dynamically evaluate packaged foods based on multiple independent vectors.

The final score is out of **100 points** and is derived from a weighted calculation:

1. **Nutrition (50% Weight)**: Evaluates the macroscopic health data of the product. Specifically monitors calories, fat, saturated fat, sodium, and sugars against recommended FDA/WHO limits.
2. **Ingredients (30% Weight)**: Parses the raw ingredients list using an NLP tree-builder. It penalizes harmful additives, artificial preservatives, and tracks ingredient quality. It also outputs a `confidence` score based on the percentage of ingredients successfully canonicalized against our database.
3. **Context (20% Weight)**: Applies contextual modifiers such as the NOVA classification (Processing Level). NOVA 1 (unprocessed) yields a perfect context score, whereas NOVA 4 (ultra-processed) severely penalizes the product.

### The "Color Status" and UI Borders
Based on the final 100-point score, the engine computes a `color_status` representing the product's safety band:
- **GREEN (Score 70 - 100)**: Excellent choice, minimal harmful additives, highly nutritious.
- **YELLOW (Score 40 - 69)**: Moderate choice, likely some processing or elevated sugars/sodium.
- **RED (Score 0 - 39)**: Poor choice, highly processed or severely unhealthy.

This `color_status` is propagated to the Next.js frontend, dynamically wrapping product images in striking Green, Yellow, or Red borders for immediate visual communication.

---

## Safe Consumption Limits & Safety Violations 🚨

To ensure consumer safety, GudFud enforces strict FDA / WHO consumption limits on ingredients.

### Schema Design
The `Ingredient` SQLAlchemy model incorporates three critical fields:
- `daily_limit_amount`: The numerical cap for a single day (e.g., 2300 for Sodium, 50 for Sugars).
- `daily_limit_unit`: The unit of measurement (e.g., "mg", "g").
- `is_generally_safe`: A boolean flag denoting if the ingredient has severe warnings attached.

### The Penalty System
If an ingredient exceeds its daily limit, the ML Engine triggers a severe penalty during evaluation:
1. The product's overall rating is instantly slashed by **25 points**.
2. The product's `color_status` is forced to **RED** regardless of other merits.
3. A `RatingSafetyViolation` record is generated in the database, tying the specific `Rating` to the offending `Ingredient`.

---

## Frontend Architecture (Next.js) 💻

The Next.js web application (`apps/web/`) is tailored to present the data transparently to the user.

- **Landing Page & "How We Grade"**: The homepage prominently features a `recharts`-powered Pie Chart that breaks down the 100-point scoring algorithm, replacing standard "recent products" feeds to prioritize education over commerce.
- **Educational Ingredient Pages (`/ingredients/[slug]`)**: GudFud hosts dedicated, SEO-friendly pages for individual ingredients. These pages bypass standard product ratings in favor of a "Safety Profile" block detailing the technical function, scientific evidence (`IngredientEvidence`), and the established safe daily limits (`is_generally_safe`, `daily_limit_amount`).

---

## Setup and Scripts

### Environment Variables
Set up your backend `.env` based on `.env.example`. Make sure `DATABASE_URL` is pointing to your PostgreSQL instance. 
For the frontend, configure `NEXT_PUBLIC_API_URL` to point to the FastAPI server.

### Populating Safe Limits
Run the initial seed script to populate base safe consumption limits (Sodium, Sugar, Saturated Fat, etc.) and generate baseline educational evidence.
```bash
python scripts/populate_safe_limits.py
```

### Running the Frontend
```bash
cd apps/web
npm install
npm run dev
```

### Database Migrations
Modifications to the scoring system require running Alembic migrations. Ensure your database is running before executing:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
