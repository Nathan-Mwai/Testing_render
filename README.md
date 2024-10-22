## Restaurant Order Management System
## Overview
This project models a restaurant order management system, capturing relationships between users, restaurants, orders, and menu items. It reflects a real-world scenario where customers can place orders at various restaurants, each with its own set of menu items.

The system includes the following key relationships:

## One-to-Many Relationships:

User → Order: A user can place multiple orders, but each order belongs to one user.
Restaurant → Order: A restaurant can have multiple orders, but each order belongs to one restaurant.
Restaurant → Menu Item: A restaurant can have many menu items, but each menu item belongs to one restaurant.
Order → Order Item: An order can have many order items, but each order item belongs to one order.
Many-to-Many Relationships:

Order ↔ Menu Item (through Order Item): An order can contain multiple menu items, and a menu item can appear in multiple orders. The link between these two is the Order Item, which serves as an intermediary table that associates orders with menu items.
Entities and Relationships
## User
Represents a customer who places orders.
Attributes: id, name, email
Relationships: A user can have many orders (One-to-Many relationship with Order).
## Restaurant
Represents a restaurant offering menu items for orders.
Attributes: id, name, location
Relationships:
A restaurant can have many orders (One-to-Many relationship with Order).
A restaurant can have many menu items (One-to-Many relationship with Menu Item).
##  Order
Represents an order placed by a user at a restaurant.
Attributes: id, order_date, total_price, user_id, restaurant_id
Relationships:
Each order is linked to a single user (Many-to-One relationship with User).
Each order is linked to a single restaurant (Many-to-One relationship with Restaurant).
An order can have many order items (One-to-Many relationship with Order Item).
## Menu Item
Represents a dish or item offered by a restaurant.
Attributes: id, name, price, restaurant_id
Relationships:
Each menu item belongs to a single restaurant (Many-to-One relationship with Restaurant).
A menu item can appear in multiple orders (Many-to-Many relationship with Order through Order Item).
## Order Item
Represents the specific items within an order, linking menu items to the order.
Attributes: id, order_id, menu_item_id, quantity
Relationships:
An order item links a single order to a single menu item (Many-to-One relationships with both Order and Menu Item).
Data Relationships Summary
One-to-Many Relationships:

User → Order: A user can place multiple orders.
Restaurant → Order: A restaurant can receive many orders.
Restaurant → Menu Item: A restaurant can offer multiple menu items.
Order → Order Item: An order can contain many order items.
Many-to-Many Relationship:

Order ↔ Menu Item: An order can contain multiple menu items, and a menu item can be part of multiple orders (linked through Order Item).
Project Structure
bash
Copy code
.
├── models.py          # Defines the database models and their relationships
├── database_setup.sql # SQL script to create the database schema
├── app.py             # Main application file with the CRUD logic
├── requirements.txt   # List of dependencies
└── README.md          # Project documentation (this file)
Technologies Used
Python: Core programming language used for building the system.
SQL (SQLite/PostgreSQL): Database management and query execution.
Flask (Optional): Web framework for building the RESTful API.
SQLAlchemy (Optional): ORM to manage database relationships, if needed.
How to Run the Project
Install Dependencies: Install the necessary Python packages by running:

bash
Copy code
pip install -r requirements.txt
Set Up the Database: Create the database schema using the provided SQL script:

bash
Copy code
sqlite3 restaurant_orders.db < database_setup.sql
Run the Application: If a web-based application is developed, you can start the Flask app by running:

bash
Copy code
python app.py
Interacting with the System: Once the system is running, you can create users, restaurants, menu items, and place orders using either the API or directly through the database.

## Author
Nathan Mwai
Alvin Kiptoo
Nathan Mbau
Brian Victor







