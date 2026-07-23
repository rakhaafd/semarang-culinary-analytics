-- Mencari restoran dengan rating tinggi (>= 4.5) namun harganya terjangkau (Price Level 1 atau 2)
SELECT 
    name, 
    category, 
    rating, 
    price_category
FROM 
    restaurants_semarang
WHERE 
    rating >= 4.5 
    AND price_level_1_4 IN (1, 2)
ORDER BY 
    rating DESC, 
    price_level_1_4 ASC;
