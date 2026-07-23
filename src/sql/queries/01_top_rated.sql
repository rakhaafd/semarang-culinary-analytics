-- Menampilkan 10 restoran dengan rating tertinggi yang memiliki lebih dari 100 ulasan
SELECT 
    name, 
    category, 
    rating, 
    reviews, 
    address
FROM 
    restaurants_semarang
WHERE 
    reviews >= 100 
    AND rating IS NOT NULL
ORDER BY 
    rating DESC, 
    reviews DESC
LIMIT 10;