SELECT i.slug, i.canonical_name, count(li.id) as freq 
FROM ingredient i 
LEFT JOIN label_ingredient li ON i.id = li.ingredient_id
WHERE i.public_summary IS NULL OR i.image_url IS NULL
GROUP BY i.slug, i.canonical_name 
ORDER BY freq DESC 
LIMIT 300;
