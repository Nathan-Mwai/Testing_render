from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData, func
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt
metadata = MetaData()
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()

class Menu_item(db.Model, SerializerMixin):
    __tablename__ = 'menu_items'
    serialize_rules = ('-restaurant.menu_items', '-order_items.menu_item',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # Validation
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    # validation
    image = db.Column(db.String)
    # validation
    
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    
    restaurant = db.relationship("Restaurant", back_populates="menu_items")
    order_items = db.relationship('Order_Item', back_populates="menu_item", cascade="all, delete-orphan")

class Order_Item(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    serialize_rules = ('-order.order_items', '-menu_item.order_items',)
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    # validation
    
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
    # validation
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
    # constraint
    address = db.Column(db.String)
    cuisine = db.Column(db.String)
    # validation
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
    # constraints
    email = db.Column(db.String, unique=True)
    # validation
    _password_hash = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    phone_number = db.Column(db.String)
    # validations
    payment_information = db.Column(db.String)
    # validations
    
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')
        
    @property
    def password(self):
        raise Exception('Password cannot be viewed.')

    @password.setter
    def password(self, password):
        self.password_hash = password

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))