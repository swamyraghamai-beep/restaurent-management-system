# Restaurant Management System
## DBMS Project Report

### 1. Abstract
The Restaurant Management System is a relational database project designed to organize common restaurant information in a structured and consistent way. It maintains customer and employee details, dining tables, menu categories, menu items, orders, order details, and payment records. MySQL is used to define relationships, enforce data integrity, and support reports through SQL queries, views, and a stored procedure.

### 2. Problem Statement
Managing menus, customer orders, tables, and payments manually can lead to duplicate records, calculation mistakes, and difficulty retrieving past order information. A centralized database is required to store these records reliably and make routine information retrieval easier.

### 3. Objectives
- Store customer, employee, table, and menu information.
- Organize menu items by category.
- Record orders and the items included in each order.
- Maintain payment status and method.
- Generate itemized bills and sales summaries using SQL.
- Demonstrate primary keys, foreign keys, constraints, joins, aggregate functions, views, transactions, and stored procedures.

### 4. Scope
The project covers the database layer for a small restaurant. It provides sample data and queries for common operations. It does not include a browser-based interface, live payment gateway, inventory purchasing, or production authentication.

### 5. Software and Hardware Requirements
**Software:** Windows/Linux/macOS, MySQL Server 8.0+, MySQL Workbench (recommended).

**Hardware:** A computer capable of running MySQL; 4 GB RAM or more is recommended for a comfortable development experience.

### 6. Modules
1. **Customer Management:** stores customer contact information.
2. **Employee Management:** stores employee names, roles, salary, and hire date.
3. **Table Management:** tracks table number, capacity, and status.
4. **Menu Management:** organizes items into categories and stores prices and availability.
5. **Order Management:** links an order to a customer, table, and employee where applicable.
6. **Order Details:** records each ordered item, quantity, and unit price at the time of ordering.
7. **Payment Management:** records amount, method, status, and a transaction reference.
8. **Reports:** provides order totals, paid revenue, pending payments, and popular items.

### 7. Database Design
The database is named `RestaurantDB`. It contains eight tables: `Customers`, `Employees`, `RestaurantTables`, `Categories`, `MenuItems`, `Orders`, `OrderDetails`, and `Payments`.

Primary keys uniquely identify rows. Foreign keys connect orders to customers, tables, and employees; menu items to categories; order details to orders and menu items; and payments to orders. Unique constraints prevent duplicate customer phone/email values, table numbers, category names, and repeated menu items within the same order. Check constraints validate non-negative prices and salaries and positive quantities/capacities.

### 8. Relationships
- One customer may place many orders; an order may also be a walk-in order with no customer linked.
- One employee may handle many orders.
- One restaurant table may be referenced by multiple orders over time.
- One category contains many menu items.
- One order contains one or more order-detail rows.
- One menu item can appear in many order-detail rows.
- Each order can have at most one payment record in this model.

### 9. Normalization
The schema is designed to approximately satisfy Third Normal Form (3NF):
- **1NF:** attributes are atomic; multiple items are stored as separate `OrderDetails` rows rather than a list in `Orders`.
- **2NF:** non-key attributes in each table depend on the table's full primary key. The `OrderDetails` table uses its own primary key and a unique constraint on `(order_id, item_id)`.
- **3NF:** category names are stored in `Categories` rather than repeated for every menu item, and customer information is stored separately from orders.

### 10. Sample SQL Operations
The included query file demonstrates menu listing with joins, order lookup, itemized billing, order subtotals, maximum-priced item lookup, total paid revenue, top-selling items, pending payment reports, order status counts, price-based searches, updates, and transaction rollback.

### 11. Testing
After running the schema and sample-data scripts, verify that eight tables exist. Run the menu view and order bill view. Test the JOIN queries, subtotal calculation, and paid-revenue query. The sample data should show paid revenue of 850.00. Before using any payment update, confirm that payment was actually received.

### 12. Advantages
- Centralized, structured storage.
- Reduced duplication through relational design.
- Improved consistency through keys and constraints.
- Faster reporting with joins, indexes, and views.
- Demonstrates essential DBMS concepts in a practical scenario.

### 13. Limitations
This is a SQL database project rather than a complete deployed restaurant product. It has no user interface, multi-user application permissions, stock management, tax configuration, real payment processing, or automated table-reservation conflict checks.

### 14. Future Enhancements
- Add a web interface with role-based authentication.
- Add inventory and ingredient tracking.
- Add tax, discount, and service-charge rules.
- Add reservations and table availability validation.
- Connect a real payment provider in a secure test environment.
- Add daily/monthly reports and backup automation.

### 15. Conclusion
The Restaurant Management System demonstrates how a relational database can organize core restaurant operations. It uses related tables, keys, constraints, SQL queries, views, and a stored procedure to support common data entry and reporting tasks. The design can be extended into a full-stack application in future work.
