One-to-Many Relationships
User to Order

A User can have many Orders.
Each Order belongs to one User.
Restaurant to Order

A Restaurant can have many Orders.
Each Order belongs to one Restaurant.
Restaurant to Menu Item

A Restaurant can have many Menu Items.
Each Menu Item belongs to one Restaurant.
Order to Order Item

An Order can have many Order Items.
Each Order Item belongs to one Order.
Many-to-Many Relationships
Order and Menu Item
An Order Item links Menu Items to Orders.
A Menu Item can appear in many Orders (through multiple Order Items).
An Order can contain many Menu Items (through multiple Order Items).
Summary of Relationships
One-to-Many Relationships:

User → Order
Restaurant → Order
Restaurant → Menu Item
Order → Order Item
Many-to-Many Relationship:

Order ↔ Menu Item (through Order Item)