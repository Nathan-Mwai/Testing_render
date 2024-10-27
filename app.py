# We are importing the required methods from here since we wanted to first understand how to import easily .
# We did not use config.py for that matter
from flask import Flask, request, make_response, session
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from models import db, Menu_item, Order_Item, Order, Restaurant, User, bcrypt
import os
from sqlalchemy.exc import IntegrityError
# I'll be using this for authorization
from functools import wraps
# The method here allows the .env to be accessed by the required recipients
from dotenv import load_dotenv

load_dotenv()

print(os.environ.get("DATABASE_URI"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app, resources={r"/restaurants": {"origins": "http://localhost:3000"}})

migrate = Migrate(app, db)
api=Api(app)
db.init_app(app)
# Using bycrpt to hide the data
bcrypt.init_app(app)

class Running_Test(Resource):
    def get(self):
        return f'<h2>I am working</h2>'

class Signup(Resource):
    def post(self):
        # Corrected is request.is_json from request.is_json()
        data = request.get_json() if request.is_json else request.form
        if "name" not in data or "password" not in data or "role" not in data:
            # We are using the session method to verify the method of the user
            return {"error": "Missing inputs required"}, 422
        if data['role'] not in ['admin', 'client', 'restaurant_owner']:
            return {"error": "Invalid role"}, 422
        # Trying to apply make a signup
        try:
            user = User(
                name=data['name'],
                email=data['email'],
                address=data['address'],
                phone_number=data['phone_number'],
                payment_information=data['payment_information'],
                role=data['role'] 
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return make_response(user.to_dict(), 201)
            # If an error occurs then it will do as below
        except IntegrityError:
            return {"error": "Username already exists"}, 422
        except Exception as e:
            print(e)
            return make_response({"error": str(e)}, 422)

        
class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter_by(id=session["user_id"]).first()
            return make_response(user.to_dict(), 200)
        else:
            return make_response({"error": "You are not logged in"}, 401)
        
class Login(Resource):
    def post(self):
        # Corrected is request.is_json from request.is_json()
        data = request.get_json() if request.is_json else request.form
        if "name" not in data or "password" not in data:
            return {"error": "Missing required fields"}, 422
        
        user = User.query.filter_by(name=data["name"]).first()
        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return make_response({'user':f"{user.name} has logged in"}, 201)
        else:
            return make_response({"error": "Username or password incorrect"}, 401)

class Logout(Resource):
    def delete(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            # Just like in the arrays and dictionaries this is used to remove an element from the session
            session.pop("user_id", None) 
            return make_response({"message": f"{user.name} has logged out"}, 204)
        else:
            return make_response({"error": "You are not logged in"}, 401)



def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return make_response({"error": "You are not logged in"}, 401)
            
            user = User.query.get(session['user_id'])
            if user.role != required_role:
                return make_response({"error": "Access forbidden: insufficient permissions"}, 403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
     
class RestaurantResource(Resource):
    # This method is working well
    def get(self, id=None):
        if id is None:
            restaurants = [restaurant.to_dict(rules=('-menu_items',"-orders",)) for restaurant in Restaurant.query.all()]
            return make_response(restaurants, 200)
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"message": "Restaurant not found"}, 404)
        return make_response(restaurant.to_dict(rules=('-menu_items',"-orders",)), 200)
    
    @role_required('restaurant_owner')
    def post(self):
        # Corrected this is request.is_json from request.is_json()
        data = request.get_json() if request.is_json else request.form
        new_restaurant = Restaurant(
            name=data['name'],
            address=data['address'],
            cuisine=data['cuisine'],
            menu=data['menu'],
            rating=data['rating'],
            reviews=data['reviews'],
        )
        db.session.add(new_restaurant)
        db.session.commit()
        
        return make_response(new_restaurant.to_dict(), 201)
    
    @role_required('restaurant_owner')
    def patch(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"message": "Restaurant not found"}, 404)

        data = request.get_json() if request.is_json else request.form
        # Update only the fields provided in the request
        if 'name' in data:
            restaurant.name = data['name']
        if 'address' in data:
            restaurant.address = data['address']
        if 'cuisine' in data:
            restaurant.cuisine = data['cuisine']
        if 'menu' in data:
            restaurant.menu = data['menu']
        if 'rating' in data:
            restaurant.rating = data['rating']
        if 'reviews' in data:
            restaurant.reviews = data['reviews']

        db.session.commit()
        return make_response(restaurant.to_dict(), 200)

class RestaurantMenu(Resource):
    def get(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)  
        if not restaurant:
            return {'message': 'There is no menu for this restaurant yet'}, 404
        
        menu_items = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'image': item.image
            }
            for item in restaurant.menu_items
        ]
        
        return make_response({
            'restaurant_id': restaurant.id,
            'restaurant_name': restaurant.name,
            'menu_items': menu_items
        })

class RestaurantOrders(Resource):
    def get(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return {"message": "There is no order in the restaurant yet"}, 404
        
        orders = [
            {'id': order.id,
            'status': order.status,
            'delivery_time': order.delivery_time,
            'deliver_address': order.delivery_address
            }
            for order in restaurant.orders 
        ]
        
        return make_response(
            {
            'restaurant_id': restaurant.id,
            'restaurant_name': restaurant.name,
            'orders':orders
            }
        )

class ClearSession(Resource):
   def delete(self):
       session['user_id']=None
       
       return {},204 
class AdminResource(Resource):
    @role_required('admin')
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response({"error": "User not found"}, 404)

        db.session.delete(user)
        db.session.commit()
        return make_response({}, 204)

class UserOrders(Resource):
    def get(self):
        if 'user_id' not in session:
            return make_response({"error": "You are not logged in"}, 401)
        
        user_id = session['user_id']
        orders = Order.query.filter_by(user_id=user_id).all()
        
        if not orders:
            return make_response({"message": "No orders found for this user"}, 404)

        orders_list = [
            {
                'id': order.id,
                'status': order.status,
                'total_price': order.total_price,
                'delivery_time': order.delivery_time,
                'delivery_address': order.delivery_address
            } for order in orders
        ]
        return make_response({'user_id': user_id, 'orders': orders_list}, 200)
    
api.add_resource(UserOrders, '/user/orders')
api.add_resource(AdminResource, '/admin/user/<int:user_id>')
api.add_resource(RestaurantMenu, '/restaurant/<int:restaurant_id>/menu')    
api.add_resource(RestaurantOrders, '/restaurant/<int:restaurant_id>/order')    
api.add_resource(RestaurantResource, '/restaurants', '/restaurants/<int:id>')
api.add_resource(Logout, "/logout", endpoint="logout")   
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Signup, '/signup')
api.add_resource(Running_Test, '/')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
