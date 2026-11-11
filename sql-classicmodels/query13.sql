SELECT customers.CustomerName, ROUND(SUM(payments.amount), 2) AS total 
FROM customers 
JOIN payments ON customers.customerNumber = payments.customerNumber 
GROUP BY customers.customerNumber, customers.customerName;