UPDATE label_ingredient
SET ingredient_id = i.id
FROM ingredient i
WHERE trim(BOTH '-' FROM regexp_replace(lower(trim(label_ingredient.label_text)), '[^a-z0-9]+', '-', 'g')) = i.slug
AND label_ingredient.ingredient_id IS NULL;
