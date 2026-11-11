SELECT employees.firstName, employees.lastName, ROUND(SUM(payments.amount), 2) AS total 
FROM employees 
JOIN customers ON employees.employeeNumber = customers.salesRepEmployeeNumber 
JOIN payments ON payments.customerNumber = customers.customerNumber 
WHERE employees.officeCode = 7 
GROUP BY employees.employeeNumber, employees.firstName, employees.lastName;