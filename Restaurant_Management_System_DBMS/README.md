# Restaurant Management System — DBMS Project

A college-level relational database project built with **MySQL 8.0+**. This is the DBMS/SQL version (not a web application). It models customers, employees, restaurant tables, categories, menu items, orders, order line items, and payments.

## Project contents

- `sql/01_schema.sql` — database and table creation, keys, constraints, and indexes
- `sql/02_sample_data.sql` — sample records for testing
- `sql/03_queries.sql` — common SELECT, JOIN, aggregate, update, and transaction examples
- `sql/04_views_procedure.sql` — reporting views and a stored procedure to create a simple order
- `documentation/ER_DIAGRAM.md` — ER diagram source in Mermaid
- `documentation/PROJECT_REPORT.md` — report content for college submission

## Requirements

- MySQL Server 8.0 or newer
- MySQL Workbench (recommended) or MySQL command-line client

## Run in MySQL Workbench

1. Install and start MySQL Server.
2. Open MySQL Workbench and connect to your local MySQL server.
3. Open `sql/01_schema.sql` and execute the entire script.
4. Open and execute `sql/02_sample_data.sql`.
5. Open and execute `sql/03_queries.sql` in sections. Note that it includes a demonstration `UPDATE` and a transaction that ends in `ROLLBACK`.
6. Open and execute `sql/04_views_procedure.sql` to create the views and stored procedure.
7. Verify the database with:

```sql
USE RestaurantDB;
SHOW TABLES;
SELECT * FROM vw_menu_with_category;
SELECT * FROM vw_order_bill;
```

## Run with the MySQL command line

From a terminal in the project folder, run the following commands, entering your MySQL password when prompted:

```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_sample_data.sql
mysql -u root -p < sql/04_views_procedure.sql
```

Run `sql/03_queries.sql` interactively in Workbench, or execute selected queries individually.

## Important notes

- The schema script drops and recreates these project tables. Do not run it against a database containing data you need to keep.
- Sample payment records are illustrative only; they are not real transactions.
- The stored procedure creates an order containing one menu item and validates the item and quantity. It is a learning example, not a production ordering system.
- This is a database project and does not include a graphical frontend or application login.
