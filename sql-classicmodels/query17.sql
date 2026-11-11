SELECT productCode, SUM(quantityOrdered) AS Total 
FROM orderdetails 
GROUP BY productCode
ORDER BY total DESC 
LIMIT 1;