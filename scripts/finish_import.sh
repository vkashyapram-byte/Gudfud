#!/bin/bash
source .venv/bin/activate
export DATABASE_URL="postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"

echo "Waiting for fast import to finish..."
while pgrep -f "import_csv_fast.py" > /dev/null; do
    sleep 5
done

echo "Fast import finished! Running fetch_images.py..."
python scripts/fetch_images.py

echo "Fetch images finished! Running fallback_images.py..."
python scripts/fallback_images.py

echo "ALL DONE!"
