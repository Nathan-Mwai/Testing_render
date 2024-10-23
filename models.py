# We are importing the required methods from here since we wanted to first understand how to import easily .
# We did not use config.py for that matter
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
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    image = db.Column(db.String)
    
    @validates('price')
    def positive_number(self, _, value):
        if not 1 <= value:
            raise ValueError("Prices must be positive")
        return value
    
    @validates('image')
    def image_availability(self, _, value):
        if not value:
            return ValueError("Meal image must be present for integrity")
        return value
    
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
    
    @validates('price')
    def positive_number(self, _, value):
        if not 1 <= value:
            raise ValueError("Prices must be positive")
        return value

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
    
    @validates('total_price')
    def positive_number(self, _, value):
        if not 1 <= value:
            raise ValueError("Prices must be positive")
        return value

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'
    
    serialize_rules = ('-orders.restaurant', '-menu_items.restaurant',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    cuisine = db.Column(db.String, nullable=False)
    menu = db.Column(db.String)
    rating = db.Column(db.String)
    reviews = db.Column(db.String)
    
    orders = db.relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = db.relationship("Menu_item", back_populates="restaurant", cascade="all, delete-orphan")
    
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-orders.user',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    phone_number = db.Column(db.String)
    payment_information = db.Column(db.String)
    role = db.Column(db.String, nullable=False)
    
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
        
    @validates('_password_hash')
    def validate_password_hash(self, key, password_hash):
        if not password_hash:
            raise ValueError("Password hash is required.")
        return password_hash
    
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required.")
        if not isinstance(email, str) or '@' not in email:
            raise ValueError("Invalid email format.")
        return email
    
    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number and (not isinstance(phone_number, str) or len(phone_number) < 10):
            raise ValueError("Phone number must be at least 10 digits.")
        return phone_number
