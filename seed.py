from faker import Faker
from models import db, User, Restaurant, Menu_item, Order, Order_Item, bcrypt
import random

# Initialize Faker
fake = Faker()
# Function to create fake users
def create_fake_users(num):
    for _ in range(num):
        # Generate a random password
        password = fake.password()

        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            address=fake.address(),
            phone_number=fake.phone_number(),
            payment_information=fake.credit_card_number(),
        )
        user.password = password 
        db.session.add(user)
    db.session.commit()

# Function to create fake restaurants
def create_fake_restaurants(num):
    for _ in range(num):
        restaurant = Restaurant(
            name=fake.company(),
            address=fake.address(),
            cuisine=random.choice(['Italian', 'Chinese', 'Indian', 'Mexican', 'American']),
            menu='Menu items will be defined separately',
            rating=str(random.randint(1, 5)),
            reviews=fake.text(max_nb_chars=200)
        )
        db.session.add(restaurant)
    db.session.commit()

# Function to create fake menu items
def create_fake_menu_items(num, restaurant_ids):
    for _ in range(num):
        menu_item = Menu_item(
            name=fake.word(),
            description=fake.sentence(),
            price=random.randint(5, 50),
            image=fake.image_url(),
            restaurant_id=random.choice(restaurant_ids)
        )
        db.session.add(menu_item)
    db.session.commit()

# Function to create fake orders
def create_fake_orders(num, user_ids, restaurant_ids):
    orders = []  
    for _ in range(num):
        order = Order(
            status=random.choice(['Pending', 'Completed', 'Cancelled']),
            total_price=random.randint(20, 200),
            delivery_time=fake.date_time_this_month(),
            delivery_address=fake.address(),
            user_id=random.choice(user_ids),
            restaurant_id=random.choice(restaurant_ids)
        )
        db.session.add(order)
        orders.append(order)  
    db.session.commit()  
    return [order.id for order in orders]  


# Function to create fake order items
def create_fake_order_items(num, order_ids, menu_item_ids):
    for _ in range(num):
        order_item = Order_Item(
            quantity=random.randint(1, 5),
            price=random.randint(5, 50),
            order_id=random.choice(order_ids),
            menu_item_id=random.choice(menu_item_ids)
        )
        db.session.add(order_item)
    db.session.commit()

if __name__ == '__main__':
    from app import app 

    with app.app_context():
        db.drop_all()
        # Create the database and tables
        db.create_all()

        # Create fake data
        num_users = 20
        num_restaurants = 15
        num_menu_items = 60
        num_orders = 15
        num_order_items = 30  

        create_fake_users(num_users)

        user_ids = [user.id for user in User.query.all()]

        create_fake_restaurants(num_restaurants)

        restaurant_ids = [restaurant.id for restaurant in Restaurant.query.all()]

        create_fake_menu_items(num_menu_items, restaurant_ids)

        order_ids = create_fake_orders(num_orders, user_ids, restaurant_ids)

        menu_item_ids = [menu_item.id for menu_item in Menu_item.query.all()]

        create_fake_order_items(num_order_items, order_ids, menu_item_ids)

    print("Database seeded successfully!")
