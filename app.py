from flask import Flask, request, make_response, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Menu_item, Order_Item, Order, Restaurant, User, bcrypt
import os
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# postgresql://testing_render_user:d5AgnAwbWNnqAVHbfYvKoIRgbhuquzHu@dpg-cs9p23rqf0us739k8cvg-a.oregon-postgres.render.com/testing_render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api=Api(app)
db.init_app(app)
bcrypt.init_app(app)

class Running_Test(Resource):
    def get(self):
        return f'<h2>I am working</h2>'

class Signup(Resource):
    def post(self):
        # Corrects is request.is_json from request.is_json()
        data = request.get_json() if request.is_json else request.form
        if "name" not in data or "password" not in data:
            return {"error": "Missing inputs required"},422
        try:
            user = User(
                name=data['name'],
                email=data['email'],
                address=data['address'],
                phone_number=data['phone_number'],
                payment_information=data['payment_information'],
            )
            user.password_hash=data['password']
            db.session.add(user)
            db.session.commit()
            session["user_id"]=user.id
            return make_response(user.to_dict(), 201)
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
        # Corrects is request.is_json from request.is_json()
        data = request.get_json() if request.is_json else request.form
        if "name" not in data or "password" not in data:
            return {"error": "Missing required fields"}, 422
        user = User.query.filter_by(name=data["name"]).first()
        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return make_response(user.to_dict(), 200)
        else:
            return make_response({"error": "Username or password incorrect"}, 401)

class Logout(Resource):
    def delete(self):
        if session["user_id"]:
            session["user_id"]=None
            return make_response({}, 204)
        else:
            return make_response({"error": "You are not logged in"}, 401)
        
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
    
    def post(self):
        # Corrects is request.is_json from request.is_json()
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

class ClearSession(Resource):
   def delete(self):
       session['user_id']=None
       
       return {},204 

api.add_resource(RestaurantMenu, '/restaurant/<int:restaurant_id>/menu')    
api.add_resource(RestaurantResource, '/restaurants', '/restaurants/<int:id>')
api.add_resource(Logout, "/logout", endpoint="logout")   
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Signup, '/signup')
api.add_resource(Running_Test, '/')

if __name__ == '__main__':
    app.run(port=5555, debug=True)