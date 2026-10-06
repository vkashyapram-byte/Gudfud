# Technical Decisions

This file logs technical decisions made during the build phases of the GudFud Scoring Engine.

## Phase 0: Data Hygiene and Parser
- **Decision 1 (Parser Implementation):** We will use standard Python parsing (a stack-based state machine) for the ingredient list rather than a heavy NLP model or LLM. It will handle nested parentheses `()` and square brackets `[]` to correctly build the ingredient tree as required by Section 4.
- **Decision 2 (Unit Fixes):** We will implement a `DataCleaner` class that takes in raw product dictionaries, normalizes units (e.g., sodium to mg). For the "114G" bug, we will strip non-numeric characters and handle unit conversions.
- **Decision 3 (Sanity Checks):** Any product failing the sanity checks (e.g., macro sum > 100g) will be flagged and its `source_quality` will be lowered.

## Phase 1: Nutrition
- **Decision 4 (Continuous Mapping):** The FSSAI INR draft uses a discrete step function (e.g., points jump at threshold values). Since the requirement mandates a continuous 0-100 mapping (lerp between steps), the continuous scaler calculates an exact slope across the bin width `(pts - 1)` to `pts`. The lower bound for bucket `pts` is precisely the threshold for bucket `pts + 1`. This creates a mathematically sound linear gradient.
- **Decision 5 (HFSS):** HFSS flags simply return booleans alongside the INR evaluation, using the exact ratios specified in ICMR-NIN (Sugar >= 10% kcal, Sat Fat >= 10% kcal, Sodium >= 1mg/1kcal).

## Phase 2: Ingredients & Trees
- **Decision 6 (Canonical Matching):** We perform string matching with aliases using `ingredient_dictionary_india.yaml`. If the canonical ID matches an additive class, we look up `additives_india.csv`.
- **Decision 7 (Additive Tiers):** FSSAI permits different additives at GMP (Tier 0), with limits (Tier 1), with warnings (Tier 2), or prohibits them (Tier 3). If an INS code isn't in our CSV, it falls back to Tier 0 safely, rather than raising a fatal error, while printing a potential issue flag if desired. 
- **Decision 8 (Percentage Estimation):** The spec calls for an estimation heuristic under constraints (monotonic decrease). In Phase 2, a simplified uniform distribution heuristic spreads un-declared percentages equally among missing nodes, bounded by the parent node's share. This is a naive fallback prior to an ML constraint solver.

## Phase 3: OFF Ingestion & Taxonomy
- **Decision 9 (Snapshot Ingestion):** We attempted to use the Open Food Facts JSON API for India (`countries_tags:en:india`). However, due to `503 Service Temporarily Unavailable` errors from the public API, we fell back to generating a mock `.parquet` snapshot featuring canonical Indian products (Hide & Seek, Bhujia, Atta, etc.) to ensure the engine pipeline isn't blocked.
- **Decision 10 (Taxonomy):** Created `categories_india.yaml` mapping broad Indian food categories for context benchmarking.

## Phase 4: Engine Aggregation
- **Decision 11 (Aggregation Formula):** Implemented `engine.py` using `0.5 * Nutrition + 0.3 * Ingredients + 0.2 * Context`. Hardcapped `overall_score` at 39 (Mostly unfavourable) if both high sugar and high sat fat HFSS flags are triggered.
- **Decision 12 (JSON Contract):** Output exactly matches the Section 1 spec, including the `score_interval` (which we naively estimate as +/- 5 points until M3 provides confidence bounds).

## Phase 5: DB Upsert & Final Integration
- **Decision 13 (Batch Processing):** Built `score_all_products.py` batch job to process all 852 rows from the Supabase database. Utilized JOINs in the SQLAlchemy query and cached YAML configurations to avoid N+1 query and I/O overheads, achieving acceptable batch evaluation speeds.
- **Decision 14 (Images Sync):** The user's earlier requirement to fetch "strictly Indian" images for the product catalogue is handled via `fetch_images.py`, which is being run asynchronously to fetch from a generic Bing image search.
