-- Menghitung jumlah restoran, rata-rata rating, dan total ulasan per kategori
SELECT 
    category,
    COUNT(*) AS total_restaurants,
    ROUND(AVG(rating)::numeric, 2) AS average_rating,
    SUM(reviews) AS total_reviews
FROM 
    restaurants_semarang
WHERE 
    category IS NOT NULL
GROUP BY 
    category
ORDER BY 
    total_restaurants DESC;
