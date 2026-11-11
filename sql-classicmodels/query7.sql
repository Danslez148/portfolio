SELECT city, postalCode 
FROM offices 
WHERE (country = 'USA' OR country = 'UK');