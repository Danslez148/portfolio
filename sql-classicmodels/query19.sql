SELECT ROUND(SUM(orderdetails.priceEach*orderdetails.quantityOrdered), 2) AS totalCost 
FROM orderdetails 
JOIN orders ON orderdetails.orderNumber = orders.orderNumber 
WHERE orders.customerNumber = '121';