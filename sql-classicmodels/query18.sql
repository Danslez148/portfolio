SELECT email 
FROM employees 
WHERE jobTitle = 'Sales Rep' 
AND employeeNumber IN (
SELECT salesRepEmployeeNumber FROM customers WHERE salesRepEmployeeNumber != 1166 GROUP BY salesRepEmployeeNumber 
HAVING COUNT(*) < (SELECT COUNT(*) FROM customers WHERE salesRepEmployeeNumber = 1166)
);