# GudFud Data Integrity & Seed Script Rule

When working on GudFud's data ingestion or modifying the `scripts/import_openfoodfacts.py` script, adhere to the following rules:

## Deduplication and Synonyms
- Many food products in India list ingredients in multiple languages or use synonyms (e.g. "Refined Wheat Flour" and "Maida"). 
- Optical Character Recognition (OCR) systems (like Open Food Facts) often split these synonyms into separate duplicate ingredient entries.
- **Rule**: You MUST ensure that ingredients are deduplicated before insertion into the `LabelIngredient` table.
- **Methodology**: The import script deduplicates ingredients by ensuring that if two ingredients map to the exact same *Canonical Ingredient* ID (e.g., both "wheat flour" and "maida" map to `wheat_flour.id`), only the first occurrence is kept. It also strips exact string duplicates (e.g. multiple "Sugar" entries if they refer to sub-ingredients).

## Data Purity
- Do not invent ingredient percentages. The percentages should exclusively be sourced from `declared_percent` extracted directly from the food label.
- When expanding `canonical_map`, ensure synonyms are grouped accurately to a single source of truth ingredient.
