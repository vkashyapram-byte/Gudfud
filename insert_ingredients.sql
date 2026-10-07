INSERT INTO ingredient (id, slug, canonical_name, ingredient_type, public_summary, status)
SELECT 
    gen_random_uuid(),
    trim(BOTH '-' FROM regexp_replace(lower(trim(label_text)), '[^a-z0-9]+', '-', 'g')),
    trim(label_text),
    'Unknown',
    'Information for ' || trim(label_text) || ' will be populated later.',
    'active'
FROM (SELECT DISTINCT label_text FROM label_ingredient WHERE label_text IS NOT NULL AND trim(label_text) != '') AS unique_labels
ON CONFLICT (slug) DO NOTHING;
