SELECT customers.customerName, customers.phone 
FROM customers 
LEFT JOIN payments ON customers.customerNumber = payments.customerNumber 
GROUP BY customers.customerNumber 
HAVING COUNT(amount) = 0;