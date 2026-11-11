SELECT products.productName, products.quantityInStock, productlines.textDescription 
FROM products 
JOIN productlines ON products.productLine = productlines.productLines 
WHERE products.quantityInStock < 100;