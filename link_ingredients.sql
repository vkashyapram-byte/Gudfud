UPDATE label_ingredient
SET ingredient_id = i.id
FROM ingredient i
WHERE trim(label_ingredient.label_text) = i.canonical_name
AND label_ingredient.ingredient_id IS NULL;
