"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, Blueprint
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Buyer
#from flask_appbuilder.api import BaseApi, expose

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


#bpr = Blueprint('register', __name__, url_prefix='/register')
#bpa = Blueprint('auth', __name__, url_prefix='/auth')

# generate sitemap with all your endpoints
@app.route('/register-buyer',  methods=['POST'])
def register_buyer():
    """ Recive data to create a Buyer """
    request_body = request.json 
    print(request.data)
    print(request.json)
    new_user = User.create(
        username = request_body["username"],
        email = request_body["email"],
        password = request_body["password"],
        is_active = True
    )
    new_user.save()
    new_buyer = Buyer.create(
        id_number = request_body["id_number"],
        first_name =request_body["first_name"],
        last_name = request_body["last_name"],
        address = request_body["address"],
        user_id = new_user.id
    )
    new_buyer.save()
    response_body = jsonify({
        "user": new_user.serialize(),
        "buyer": new_buyer.serialize()
    })
        #email = request_body["full_name"], 
    # new_buyer = Buyer.create(
    #     full_name = request_body["full_name"], 
    #     email = request_body["email"],
    #     address = request_body["address"],
    #     phone = request_body["phone"]
    # )
    return response_body, 200
    #return jsonify(response_body), 200



@app.route('/profile-buyer',  methods=['GET'])
def get_buyer():
    response_body = {
            "id":"45",
            "email":"miguel@email.com",
            "role": "My Role"
    }
    return jsonify(response_body), 200



# generate sitemap with all your endpoints
# @app.route('/')
# def sitemap():
#     return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
