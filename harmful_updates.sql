UPDATE ingredient SET is_generally_safe = false, public_summary = 'Aspartame is an artificial non-saccharide sweetener used as a sugar substitute. While approved by many agencies, the WHO''s IARC classified aspartame as ''possibly carcinogenic to humans'' (Group 2B) in 2023, though the JECFA reaffirmed acceptable daily intake levels.' WHERE slug = 'aspartame';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'aspartame');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Possible Carcinogen', 'warning', 'Aspartame is an artificial non-saccharide sweetener used as a sugar substitute. While approved by many agencies, the WHO''s IARC classified aspartame as ''possibly carcinogenic to humans'' (Group 2B) in 2023, though the JECFA reaffirmed acceptable daily intake levels.', 'published', NOW()
    FROM ingredient WHERE slug = 'aspartame';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Sucralose is an artificial sweetener. Recent studies suggest it may alter gut microbiome composition and negatively affect glucose tolerance. Some evidence points to it causing DNA damage in high concentrations.' WHERE slug = 'sucralose';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'sucralose');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Gut Microbiome Disruption', 'warning', 'Sucralose is an artificial sweetener. Recent studies suggest it may alter gut microbiome composition and negatively affect glucose tolerance. Some evidence points to it causing DNA damage in high concentrations.', 'published', NOW()
    FROM ingredient WHERE slug = 'sucralose';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'High Fructose Corn Syrup (HFCS) is a liquid sweetener. Its high consumption is strongly linked to obesity, insulin resistance, type 2 diabetes, and non-alcoholic fatty liver disease (NAFLD).' WHERE slug = 'high-fructose-corn-syrup';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'high-fructose-corn-syrup');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Metabolic Disruption', 'harmful', 'High Fructose Corn Syrup (HFCS) is a liquid sweetener. Its high consumption is strongly linked to obesity, insulin resistance, type 2 diabetes, and non-alcoholic fatty liver disease (NAFLD).', 'published', NOW()
    FROM ingredient WHERE slug = 'high-fructose-corn-syrup';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Carrageenan is an extract from red seaweed used as a thickener. Degraded carrageenan can cause gastrointestinal inflammation and intestinal lesions. Even food-grade carrageenan is suspected by some researchers to trigger inflammation.' WHERE slug = 'carrageenan';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'carrageenan');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Gastrointestinal Inflammation', 'warning', 'Carrageenan is an extract from red seaweed used as a thickener. Degraded carrageenan can cause gastrointestinal inflammation and intestinal lesions. Even food-grade carrageenan is suspected by some researchers to trigger inflammation.', 'published', NOW()
    FROM ingredient WHERE slug = 'carrageenan';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Butylated Hydroxyanisole (BHA) is a synthetic antioxidant used as a preservative. The National Institutes of Health (NIH) considers BHA ''reasonably anticipated to be a human carcinogen'' based on animal studies.' WHERE slug = 'bha';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'bha');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Endocrine Disruptor / Possible Carcinogen', 'harmful', 'Butylated Hydroxyanisole (BHA) is a synthetic antioxidant used as a preservative. The National Institutes of Health (NIH) considers BHA ''reasonably anticipated to be a human carcinogen'' based on animal studies.', 'published', NOW()
    FROM ingredient WHERE slug = 'bha';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Butylated Hydroxytoluene (BHT) is a preservative structurally similar to BHA. Animal studies indicate potential liver enlargement and carcinogenic effects at high doses.' WHERE slug = 'bht';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'bht');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Potential Organ Toxicity', 'warning', 'Butylated Hydroxytoluene (BHT) is a preservative structurally similar to BHA. Animal studies indicate potential liver enlargement and carcinogenic effects at high doses.', 'published', NOW()
    FROM ingredient WHERE slug = 'bht';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Red 40 is a synthetic food dye. It has been associated with hypersensitivity reactions and increased hyperactivity in children. Some European countries require warning labels on foods containing it.' WHERE slug = 'red-40-allura-red-ac';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'red-40-allura-red-ac');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Hyperactivity in Children', 'warning', 'Red 40 is a synthetic food dye. It has been associated with hypersensitivity reactions and increased hyperactivity in children. Some European countries require warning labels on foods containing it.', 'published', NOW()
    FROM ingredient WHERE slug = 'red-40-allura-red-ac';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Yellow 5 (Tartrazine) is a synthetic lemon yellow azo dye. It is known to cause allergic reactions, asthma, and skin rashes in a small percentage of the population, and is linked to hyperactivity in children.' WHERE slug = 'yellow-5-tartrazine';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'yellow-5-tartrazine');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Allergic Reactions / Hyperactivity', 'warning', 'Yellow 5 (Tartrazine) is a synthetic lemon yellow azo dye. It is known to cause allergic reactions, asthma, and skin rashes in a small percentage of the population, and is linked to hyperactivity in children.', 'published', NOW()
    FROM ingredient WHERE slug = 'yellow-5-tartrazine';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Titanium Dioxide is a white pigment used to enhance color. In 2021, the European Food Safety Authority (EFSA) declared it can no longer be considered safe as a food additive due to concerns over genotoxicity (DNA damage).' WHERE slug = 'titanium-dioxide';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'titanium-dioxide');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Genotoxicity', 'harmful', 'Titanium Dioxide is a white pigment used to enhance color. In 2021, the European Food Safety Authority (EFSA) declared it can no longer be considered safe as a food additive due to concerns over genotoxicity (DNA damage).', 'published', NOW()
    FROM ingredient WHERE slug = 'titanium-dioxide';
    
UPDATE ingredient SET is_generally_safe = false, public_summary = 'Sodium Benzoate is a preservative. When combined with ascorbic acid (Vitamin C), it can form benzene, a known carcinogen. It may also exacerbate hyperactivity in children.' WHERE slug = 'sodium-benzoate';
DELETE FROM ingredient_evidence WHERE ingredient_id IN (SELECT id FROM ingredient WHERE slug = 'sodium-benzoate');

    INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, review_status, reviewed_at) 
    SELECT gen_random_uuid(), id, 'Benzene Formation Risk', 'warning', 'Sodium Benzoate is a preservative. When combined with ascorbic acid (Vitamin C), it can form benzene, a known carcinogen. It may also exacerbate hyperactivity in children.', 'published', NOW()
    FROM ingredient WHERE slug = 'sodium-benzoate';
    