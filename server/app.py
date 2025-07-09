#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        """GET /restaurants - Return all restaurants"""
        restaurants = Restaurant.query.all()
        return make_response(
            [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants],
            200
        )


class RestaurantByID(Resource):
    def get(self, id):
        """GET /restaurants/<id> - Return restaurant with pizza relationships"""
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return make_response(
                {"error": "Restaurant not found"}, 
                404
            )
        
        return make_response(
            restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas.id', 
                                   'restaurant_pizzas.price', 'restaurant_pizzas.pizza_id', 
                                   'restaurant_pizzas.restaurant_id', 'restaurant_pizzas.pizza.id', 
                                   'restaurant_pizzas.pizza.name', 'restaurant_pizzas.pizza.ingredients')),
            200
        )
    
    def delete(self, id):
        """DELETE /restaurants/<id> - Delete restaurant and associated RestaurantPizzas"""
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return make_response(
                {"error": "Restaurant not found"}, 
                404
            )
        
        db.session.delete(restaurant)
        db.session.commit()
        
        return make_response('', 204)


class Pizzas(Resource):
    def get(self):
        """GET /pizzas - Return all pizzas"""
        pizzas = Pizza.query.all()
        return make_response(
            [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas],
            200
        )


class RestaurantPizzas(Resource):
    def post(self):
        """POST /restaurant_pizzas - Create new RestaurantPizza"""
        data = request.get_json()
        
        try:
            # Create new RestaurantPizza
            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            return make_response(
                restaurant_pizza.to_dict(only=('id', 'price', 'pizza_id', 'restaurant_id',
                                             'pizza.id', 'pizza.name', 'pizza.ingredients',
                                             'restaurant.id', 'restaurant.name', 'restaurant.address')),
                201
            )
        
        except ValueError as e:
            return make_response(
                {"errors": [str(e)]},
                400
            )
        except Exception as e:
            return make_response(
                {"errors": ["validation errors"]},
                400
            )


# Add resources to API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)