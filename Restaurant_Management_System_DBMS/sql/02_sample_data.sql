USE restaurantdb;

INSERT INTO Customers (customer_name, phone, email) VALUES
('Rahul Sharma','9876543210','rahul@example.com'),
('Priya Reddy','9876543211','priya@example.com'),
('Aman Verma','9876543212','aman@example.com'),
('Sara Khan','9876543213','sara@example.com');

INSERT INTO Employees (employee_name, role, phone, salary, hire_date) VALUES
('Ravi Kumar','Manager','9000000001',30000.00,'2025-01-10'),
('Sita Devi','Chef','9000000002',25000.00,'2025-02-15'),
('Kiran Rao','Waiter','9000000003',15000.00,'2025-03-01'),
('Meena Das','Cashier','9000000004',18000.00,'2025-04-20');

INSERT INTO RestaurantTables (table_number, capacity, status) VALUES
(1,2,'Available'),(2,4,'Occupied'),(3,4,'Available'),(4,6,'Reserved'),(5,2,'Available');

INSERT INTO Categories (category_name) VALUES
('Starters'),('Main Course'),('Desserts'),('Drinks');

INSERT INTO MenuItems (item_name, category_id, description, price, available) VALUES
('Veg Manchurian',1,'Crispy vegetable balls in sauce',180.00,TRUE),
('Paneer Tikka',1,'Grilled marinated paneer',220.00,TRUE),
('Paneer Biryani',2,'Aromatic rice with paneer',250.00,TRUE),
('Chicken Biryani',2,'Spiced chicken and basmati rice',300.00,TRUE),
('Masala Dosa',2,'Crisp dosa with potato filling',120.00,TRUE),
('Ice Cream',3,'Two scoops of seasonal ice cream',100.00,TRUE),
('Gulab Jamun',3,'Two pieces in sugar syrup',80.00,TRUE),
('Fresh Lime Soda',4,'Sweet or salted lime soda',70.00,TRUE),
('Water Bottle',4,'Packaged drinking water',30.00,TRUE);

INSERT INTO Orders (customer_id, table_id, employee_id, order_type, status, notes) VALUES
(1,1,3,'Dine-in','Completed','Less spicy'),
(2,2,3,'Dine-in','Preparing','No onions'),
(3,NULL,4,'Takeaway','Pending','Pack separately'),
(4,NULL,4,'Delivery','Completed','Call on arrival');

INSERT INTO OrderDetails (order_id, item_id, quantity, unit_price) VALUES
(1,3,2,250.00),(1,6,1,100.00),
(2,4,1,300.00),(2,8,2,70.00),
(3,5,2,120.00),(3,7,1,80.00),
(4,1,1,180.00),(4,8,1,70.00);

INSERT INTO Payments (order_id, amount, payment_method, payment_status, payment_date, transaction_reference) VALUES
(1,600.00,'UPI','Paid',CURRENT_TIMESTAMP,'TXN-DEMO-1001'),
(2,440.00,'Cash','Pending',NULL,NULL),
(3,320.00,'Card','Pending',NULL,NULL),
(4,250.00,'Online','Paid',CURRENT_TIMESTAMP,'TXN-DEMO-1004');

-- Set table 1 back to Available after the completed sample order.
UPDATE RestaurantTables SET status='Available' WHERE table_number=1;
