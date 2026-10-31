-- Restaurant Management System (DBMS Project)
-- MySQL 8.0+
CREATE DATABASE IF NOT EXISTS RestaurantDB;
USE RestaurantDB;

SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS vw_order_bill;
DROP VIEW IF EXISTS vw_menu_with_category;
DROP PROCEDURE IF EXISTS sp_place_order;
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS MenuItems;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS RestaurantTables;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Customers;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(120) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    role ENUM('Manager','Chef','Waiter','Cashier') NOT NULL,
    phone VARCHAR(15) UNIQUE,
    salary DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (salary >= 0),
    hire_date DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE RestaurantTables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT NOT NULL UNIQUE,
    capacity INT NOT NULL CHECK (capacity > 0),
    status ENUM('Available','Occupied','Reserved','Maintenance') NOT NULL DEFAULT 'Available'
);

CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE MenuItems (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    description VARCHAR(255),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    available BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NULL,
    table_id INT NULL,
    employee_id INT NULL,
    order_type ENUM('Dine-in','Takeaway','Delivery') NOT NULL DEFAULT 'Dine-in',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending','Preparing','Ready','Completed','Cancelled') NOT NULL DEFAULT 'Pending',
    notes VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (table_id) REFERENCES RestaurantTables(table_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE OrderDetails (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE KEY uq_order_item (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES MenuItems(item_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    payment_method ENUM('Cash','Card','UPI','Online') NOT NULL,
    payment_status ENUM('Pending','Paid','Refunded','Failed') NOT NULL DEFAULT 'Pending',
    payment_date DATETIME NULL,
    transaction_reference VARCHAR(100) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_orders_date ON Orders(order_date);
CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_menu_category ON MenuItems(category_id);
