USE RestaurantDB;

-- 1. Display the full food menu with category names.
SELECT m.item_id, m.item_name, c.category_name, m.price, m.available
FROM MenuItems m JOIN Categories c ON c.category_id=m.category_id
ORDER BY c.category_name, m.item_name;

-- 2. List orders with customer and table details.
SELECT o.order_id, COALESCE(c.customer_name,'Walk-in customer') AS customer,
       o.order_type, rt.table_number, o.order_date, o.status
FROM Orders o
LEFT JOIN Customers c ON c.customer_id=o.customer_id
LEFT JOIN RestaurantTables rt ON rt.table_id=o.table_id
ORDER BY o.order_date DESC;

-- 3. Calculate each order's subtotal.
SELECT order_id, SUM(quantity * unit_price) AS subtotal
FROM OrderDetails GROUP BY order_id ORDER BY order_id;

-- 4. Print an itemized bill for one order (change 1 to the desired order ID).
SELECT o.order_id, c.customer_name, m.item_name, d.quantity,
       d.unit_price, d.quantity*d.unit_price AS line_total
FROM Orders o
LEFT JOIN Customers c ON c.customer_id=o.customer_id
JOIN OrderDetails d ON d.order_id=o.order_id
JOIN MenuItems m ON m.item_id=d.item_id
WHERE o.order_id=1;

-- 5. Find the most expensive menu item.
SELECT item_name, price FROM MenuItems
WHERE price=(SELECT MAX(price) FROM MenuItems);

-- 6. Total revenue from paid payments only.
SELECT COALESCE(SUM(amount),0) AS total_paid_revenue
FROM Payments WHERE payment_status='Paid';

-- 7. Top-selling items by total quantity.
SELECT m.item_name, SUM(d.quantity) AS quantity_sold
FROM OrderDetails d JOIN MenuItems m ON m.item_id=d.item_id
JOIN Orders o ON o.order_id=d.order_id
WHERE o.status <> 'Cancelled'
GROUP BY m.item_id, m.item_name
ORDER BY quantity_sold DESC, m.item_name;

-- 8. Orders whose payment is still pending.
SELECT o.order_id, p.amount, p.payment_method, p.payment_status
FROM Orders o JOIN Payments p ON p.order_id=o.order_id
WHERE p.payment_status='Pending';

-- 9. Count orders by status.
SELECT status, COUNT(*) AS order_count FROM Orders GROUP BY status;

-- 10. Search available menu items under a chosen price (example: 200).
SELECT item_name, price FROM MenuItems
WHERE available=TRUE AND price < 200 ORDER BY price;

-- 11. Update an order status.
UPDATE Orders SET status='Ready' WHERE order_id=2;

-- 12. Mark a payment as paid (example order 2; update only after actual payment).
-- UPDATE Payments SET payment_status='Paid', payment_date=CURRENT_TIMESTAMP
-- WHERE order_id=2;

-- 13. Example of a safe transaction for changing a menu price.
START TRANSACTION;
UPDATE MenuItems SET price=190.00 WHERE item_name='Veg Manchurian';
-- Review the change before choosing COMMIT or ROLLBACK.
SELECT item_name, price FROM MenuItems WHERE item_name='Veg Manchurian';
ROLLBACK;
