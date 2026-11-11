SELECT customers.customerName AS CustomerName, ROUND(SUM(payments.amount), 2) 
AS total 
FROM customers 
JOIN payments ON customers.customerNumber = payments.customerNumber
WHERE customers.city = 'Paris'
GROUP BY customers.customerNumber, customers.customerName 
HAVING COUNT(payments.amount >= 4);