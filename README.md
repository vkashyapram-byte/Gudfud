# GudFud - Transparent Food Label Analysis

GudFud is an independent AI platform that deeply analyzes packaged food products based on a rigorous 100-point scale. It features a Python FastAPI backend for Machine Learning ingestion/scoring, a PostgreSQL database (Supabase) managed via SQLAlchemy/Alembic, and a highly responsive Next.js frontend deployed on Vercel.

---

## 🎯 Project Philosophy & Architecture

GudFud aims to prioritize education and food transparency over commerce. The architecture is a modern monorepo separating the intensive ML calculations from the user interface:

- **Frontend (`apps/web/`)**: A Next.js application designed with a sleek, minimalist, monochrome UI. The design is strictly health-focused and actively avoids typical ecommerce patterns, prioritizing readability and nutritional clarity.
- **Backend (Root `src/`)**: A Python FastAPI server that serves the database API and handles the ML-driven evaluation of products. It connects to a Supabase PostgreSQL instance.
- **Database**: Managed via Alembic migrations, utilizing models for `Product`, `ProductVariant`, `LabelVersion`, `Rating`, `Ingredient`, and `NutritionFacts`.

---

## 🧠 The Scoring Engine (Detailed Breakdown)

At the core of GudFud is the scoring engine (`SimpleMLScorer`), which evaluates packaged foods using a deterministic, multi-factor heuristic model. The final score is bound between **10 to 100 points** and is derived from a weighted calculation of three independent variables: Nutrition, Ingredients, and Context.

### 1. Nutrition Score (50% Weight)
The Nutrition Score evaluates the macroscopic health data of the product, starting with a base of 100 points and penalizing excess amounts of harmful macronutrients. The formula actively targets leading causes of chronic illnesses:

- **Sugar Penalty**: Subtracts 2 points for every gram of sugar `(sugars_g * 2)`.
- **Sodium Penalty**: Subtracts 0.05 points for every milligram of sodium `(sodium_mg * 0.05)`.
- **Saturated Fat Penalty**: Subtracts 3 points for every gram of saturated fat `(saturated_fat_g * 3)`.

The resulting `nutrition_score` is then clamped between `10` and `100`.

### 2. Ingredients Score (30% Weight)
The Ingredients Score analyzes the complexity and length of the raw ingredients list. The model operates on the heuristic that heavily processed foods typically contain highly extensive ingredient lists full of synthetic additives.

- **Length Penalty**: Starting from 100 points, it subtracts 2 points for every discrete ingredient item detected in the list `(ingredient_count * 2)`.
- **Toxicity Dictionary Matrix**: The model employs a comprehensive toxicity dictionary containing both plain-text chemical names (e.g. "sucralose", "carrageenan", "sodium benzoate") and International Numbering System (INS) or E-numbers (e.g. "INS 211", "INS 955", "INS 102").
  - **Tier 1 Hazards (-20 pts)**: Severely penalizes artificial dyes, carcinogenic preservatives, and inflammatory emulsifiers. 
    - *Full list:* BHA, BHT, TBHQ, Propyl/Methyl/Ethyl Paraben, Propyl Gallate, Sodium/Potassium Nitrite, Sodium/Potassium Nitrate, Sodium/Potassium Benzoate, Calcium Sorbate, Sodium Sulfite, Sulfur Dioxide, Potassium/Sodium Bisulfite, Red 40, Yellow 5, Yellow 6, Red 3, Blue 1, Blue 2, Green 3, Titanium Dioxide, Caramel Color, Potassium Bromate, Azodicarbonamide, Benzoyl Peroxide, Chlorine Dioxide, Brominated Vegetable Oil (BVO), Carrageenan, Polysorbate 80/60, Aspartame, Sucralose, Saccharin, Acesulfame Potassium (Ace-K), Partially Hydrogenated/Interesterified Oils.
    - *INS Codes:* 211, 320, 321, 319, 924, 927a, 250, 251, 407, 951, 955, 954, 102, 110, 129, 133, 171.
  - **Tier 2 Hazards (-5 pts)**: Moderately penalizes questionable additives and heavily processed fillers.
    - *Full list:* EDTA, DATEM, Sodium Stearoyl Lactylate (SSL), Carboxymethylcellulose, Cellulose Gum, Propylene Glycol, High Fructose Corn Syrup (HFCS), Corn Syrup Solids, Maltodextrin, Agave Nectar, MSG, Hydrolyzed Soy/Vegetable Protein, Autolyzed Yeast Extract, Artificial Flavors, Diacetyl, Fully Hydrogenated Oils, Sodium/Potassium Aluminum, Silicon Dioxide, Talc.
    - *INS Codes:* 433, 202.
- The resulting `ingredient_score` is clamped between `10` and `100`.

### 3. Context Score (20% Weight)
The Context Score dynamically accounts for contextual health modifiers outside of standard macros and ingredient counts. This includes variables like processing level (e.g., NOVA classification - where NOVA 1 is unprocessed and NOVA 4 is ultra-processed). Currently, the pipeline assigns a baseline contextual variance which contributes 20% to the final outcome.

### Final Total Calculation
The engine applies the predetermined weights to generate the final `total_score`:
```python
total_score = (nutrition_score * 0.5) + (ingredient_score * 0.3) + (context_score * 0.2)
total_score = max(10, min(100, int(total_score)))
```

### Safety Bands / Color Status
Based on the final 100-point score, the engine computes a strictly defined safety band which determines the UI color-coding:
- **🟢 Mostly Favourable (Score 70 - 100)**: Excellent choice, minimal harmful additives, highly nutritious.
- **🟡 Moderate (Score 40 - 69)**: Moderate choice, likely some processing or elevated sugars/sodium.
- **🔴 Mostly Unfavourable (Score 10 - 39)**: Poor choice, highly processed or severely unhealthy.

This `band` and the `total_score` are persisted directly into the Supabase database and served via the FastAPI backend to the Next.js frontend.

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
   npx supabase db query -f get_all_prod_data.sql --linked > raw_output_all.txt
   python apply_toxicity.py
   npx supabase db query -f update_scores_toxicity_all.sql --linked
   ```
   *(Note: The `apply_toxicity.py` script leverages a Toxicity Dictionary to parse the raw ingredients, process the NLP/nutritional rules, and generates an `UPDATE` operation directly back to the database).*

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
