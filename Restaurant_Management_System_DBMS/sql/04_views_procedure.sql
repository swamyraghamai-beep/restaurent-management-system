USE RestaurantDB;

CREATE OR REPLACE VIEW vw_menu_with_category AS
SELECT m.item_id, m.item_name, c.category_name, m.description, m.price, m.available
FROM MenuItems m JOIN Categories c ON c.category_id=m.category_id;

CREATE OR REPLACE VIEW vw_order_bill AS
SELECT o.order_id, o.order_date, o.status,
       COALESCE(c.customer_name,'Walk-in customer') AS customer_name,
       COALESCE(SUM(d.quantity*d.unit_price),0) AS subtotal
FROM Orders o
LEFT JOIN Customers c ON c.customer_id=o.customer_id
LEFT JOIN OrderDetails d ON d.order_id=o.order_id
GROUP BY o.order_id, o.order_date, o.status, c.customer_name;

-- Example calls:
-- SELECT * FROM vw_menu_with_category;
-- SELECT * FROM vw_order_bill;

DELIMITER $$
CREATE PROCEDURE sp_place_order(
    IN p_customer_id INT,
    IN p_table_id INT,
    IN p_employee_id INT,
    IN p_order_type VARCHAR(20),
    IN p_item_id INT,
    IN p_quantity INT
)
BEGIN
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_order_id INT;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Quantity must be greater than zero';
    END IF;

    SELECT price INTO v_price FROM MenuItems
    WHERE item_id=p_item_id AND available=TRUE;

    IF v_price IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Menu item does not exist or is unavailable';
    END IF;

    START TRANSACTION;
    INSERT INTO Orders(customer_id, table_id, employee_id, order_type, status)
    VALUES(p_customer_id, p_table_id, p_employee_id, p_order_type, 'Pending');
    SET v_order_id=LAST_INSERT_ID();

    INSERT INTO OrderDetails(order_id, item_id, quantity, unit_price)
    VALUES(v_order_id, p_item_id, p_quantity, v_price);
    COMMIT;

    SELECT v_order_id AS created_order_id, v_price*p_quantity AS item_subtotal;
END$$
DELIMITER ;

-- Example: CALL sp_place_order(1, 1, 3, 'Dine-in', 3, 2);
