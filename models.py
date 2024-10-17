from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData, func
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class Menu_item(db.Model, SerializerMixin):
    __tablename__ = 'menu_items'
    serialize_rules = ('-restaurant.menu_items', '-order_items.menu_item',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    image = db.Column(db.String)
    
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    
    restaurant = db.relationship("Restaurant", back_populates="menu_items")
    order_items = db.relationship('Order_Item', back_populates="menu_item", cascade="all, delete-orphan")

class Order_Item(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    serialize_rules = ('-order.order_items', '-menu_item.order_items',)
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    order = db.relationship("Order", back_populates="order_items")
    menu_item = db.relationship("Menu_item", back_populates="order_items")

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    serialize_rules = ('-user.orders', '-restaurant.orders', '-order_items.order',)
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    total_price = db.Column(db.Integer)
    delivery_time = db.Column(db.DateTime, default=func.datetime('now', '+1 hour'))
    delivery_address = db.Column(db.String)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    
    user = db.relationship("User", back_populates="orders")
    restaurant = db.relationship("Restaurant", back_populates="orders")
    order_items = db.relationship('Order_Item', back_populates="order", cascade="all, delete-orphan")

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'
    
    serialize_rules = ('-orders.restaurant', '-menu_items.restaurant',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    cuisine = db.Column(db.String)
    menu = db.Column(db.String)
    rating = db.Column(db.String)
    reviews = db.Column(db.String)
    
    orders = db.relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = db.relationship("Menu_item", back_populates="restaurant", cascade="all, delete-orphan")

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-orders.user',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    _password_hash = db.Column(db.String)
    address = db.Column(db.String)
    phone_number = db.Column(db.String)
    payment_information = db.Column(db.String)
    
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")