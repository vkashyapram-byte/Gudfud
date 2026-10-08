SELECT 
    json_build_object(
        'rating_id', r.id,
        'ingredients_raw', lv.ingredients_raw,
        'sugars', nf.sugars,
        'sodium', nf.sodium,
        'saturated_fat', nf.saturated_fat,
        'product_name', p.canonical_name
    ) as data
FROM rating r
JOIN label_version lv ON r.label_version_id = lv.id
LEFT JOIN nutrition_facts nf ON nf.label_version_id = lv.id
JOIN product_variant pv ON lv.variant_id = pv.id
JOIN product p ON pv.product_id = p.id
ORDER BY p.canonical_name ASC;
