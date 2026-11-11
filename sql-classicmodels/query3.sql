SELECT productVendor, productName, quantityInStock 
FROM products 
WHERE (productVendor LIKE '%diecast%' OR productVendor LIKE '%dyecast%') 
AND quantityInStock < 2000;