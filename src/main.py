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
#Modelos de datos
from models import db, User, Buyer, Seller, Category, Store, Product, ProductToBuy
#Flask JWT Extended 
from flask_jwt_extended import create_access_token, JWTManager
#from flask_appbuilder.api import BaseApi, expose

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "317fc45bf08126c37f6cb1fd14bcdc9b"
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


#bpr = Blueprint('register', __name__, url_prefix='/register')
#bpa = Blueprint('auth', __name__, url_prefix='/auth')

# generate sitemap with all your endpoints

#----------------------------SIGNUP BUYER AND SELLER----------------------

@app.route('/signup-buyer',  methods=['POST'])
def register_buyer():
    """ Recive data to create a Buyer """
    request_body = request.json 
    print(request.data)
    print(request.json)
    new_user = User.create(
        email = request_body["email"],
        password = request_body["password"]
    )

    if not isinstance(new_user, User):
        return jsonify({
            "msg": "ocurrió un problea al crear el Usuario"
        }), 500
    new_user.save()

    new_buyer = Buyer.create(
        first_name = request_body["first_name"],
        last_name = request_body["last_name"],
        id_number = request_body["id_number"],
        cellphone_number = request_body["cellphone_number"],
        address = request_body["address"],
        user_id = new_user.id
    )
    if not isinstance(new_buyer, Buyer):
        return jsonify({
            "msg": "ocurrió un problea al crear el Usuario"
        }), 500

    new_buyer.save()

    return jsonify({
        "msg": "El usuario fue creado satisfactoriamente.",
        "user": new_user.serialize()
    }), 201
    #return jsonify(response_body), 200

@app.route('/signup-seller', methods=['POST'])
def register_seller():
    """ Recibe data to create an User and assign it to a seller, creating one """
    request_body = request.json

    #Create an user
    new_user = User(
        email =  request_body["email"],
        password = request_body["password"],
    )
    if not isinstance(new_user, User):
        return jsonify(
            {
                "msg": "Ocurrió un problema al crear el usuario."
            }
        ), 500
    new_user.save()

    #Create seller role
    seller = Seller.create(
        company_name = request_body["company_name"],
        identification_number = request_body["identification_number"],
        cellphone_number = request_body["cellphone_number"],
        user_id = new_user.id
    )
    if not isinstance(seller, Seller):
        #User.query.filter_by(id= user.id).delete()
        #db.session.commit()
        return jsonify({
            "msg" : "Ocurrió un error creando el rol de vendedor"
        }), 500

    seller.save()


    #Create Store
    store = Store.create(
        name = request_body['name'],
        description = request_body["description"],
        seller_id = seller.id
    )
    if not isinstance(store, Store):
        return jsonify({
            "msg" : "Ocurrió un problema al crear la tienda"
        }), 500
    store.save()
    return jsonify({
        "msg": "La cuenta fue creada satisfactoriamente",
        "response": {
            "user":  new_user.serialize(),
            "seller": seller.serialize(),
            "store": store.serialize()
        }
    }), 201

#------------------------------------LOGIN-------------------------------

@app.route('/login', methods=['POST'])
def log_user_in():
    """ 
        Log in a user checking password and email. Return token and info about the user
    
    """
    data = request.json
    user = User.query.filter_by(email = data.get('email')).one_or_none()
    if user is None:
        return jsonify({
            "msg" : "El usuario no existe"
        }), 404
    if not user.check_password(data.get('password')):
        return jsonigy({
            "msg" : "Malas credenciales"
        }), 404
    #Create token
    token = create_access_token(identity=user.id)

    user_role = user.role
    return jsonify({
        "user": user.serialize(),
        "role": user_role,
        "jwt": token
    }), 201


#----------------------------BUYER ENDPOINTS-------------------------

@app.route('/buyers', methods=['GET'])
def get_buyers():
    """Get all the buyers """
    buyers = Buyer.get_all()
    buyers_dict = list(map(lambda buyer: buyer.serialize(), buyers))
    return jsonify({
        "buyers": buyers_dict
    })


#----------------------------CATEGORY ENDPOINTS------------------------

@app.route('/categories', methods=['GET'])
def get_categories():
    """ Get all the categories available """
    categories = Category.get_all()
    categories_dict = list(map(lambda category: category.serialize(), categories))
    return jsonify(
        {
            "categories" : categories_dict
        }
    )

@app.route('/new-category', methods=['POST'])
def create_category():
    """ Create a new category """
    request_body = request.json
    new_category = Category.create(
        name = request_body["name"]
    )
    new_category.save()
    return jsonify(
        {
            "msg": "La categoría fue creada satisfactoriamente",
            "category": new_category.serialize()
        }
    )
#----------------------------STORE ENDPOINTS -------------------

@app.route('/<int:seller_id>/store', methods=['GET'])
def get_store(seller_id):
    """ Get a specific store by id """
    store_id = Store.query.filter_by(seller_id = seller_id).one_or_none()
    print(store_id)
    store = Store.get_by_id(store_id.id)
    return jsonify(
        {
            "store" : store.serialize()
        }
    ), 200
    

@app.route('/new-store', methods=['POST'])
def create_store():
    """ Recibe data to create a new store """
    request_body = request.json
    new_store = Store.create(
        name = request_body["name"],
        description = request_body["description"]
    )
    new_store.save()
    return jsonify(
        {
            "msg" : "La tienda fue creada satisfactoriamente",
            "store": new_store.serialize()
        }
    ), 201

@app.route('/stores', methods=['GET'])
def get_stores():
    """ Return all the stores available """
    stores = Store.get_all()
    return jsonify({
        "stores": [ store.serialize() for store in stores ]
    }), 200

#------------------------------PRODUCT ENDPOINTS--------------------

@app.route('/stores/<int:store_id>/products', methods=['GET'])
def get_all_products(store_id):
    """ Get all the poducts in a specific Store by store_id"""
    products = Product.get_by_store(store_id)
    products_dict = list(map(lambda product: product.serialize(), products))
    return jsonify(
        {
            "store_id" : store_id, 
            "products" : products_dict
        }
    ), 200
    

@app.route('/stores/<int:store_id>/new-product', methods=['POST'])
def new_product(store_id):
    """Create a new Product for a specific Store by store id """
    request_body = request.json
    new_product = Product.create(
        name = request_body["name"],
        description = request_body["description"],
        price = request_body["price"],
        amount_available = request_body['amount_available'],
        store_id = store_id,
        active = request_body['active'],
        img_url = request_body['img_url'],
        category_id = request_body['category_id']
    )
    new_product.save()
    return jsonify(
        {
            "msg" : "Su producto fue creado satisfactoriamente",
            "product" : new_product.serialize()
        }
    ), 201


#-------------------PRODUCT TO BUY -------------------
@app.route('/<int:buyer_id>/products-to-buy', methods=['GET'])
def get_products_buyer(buyer_id):
    """ Get all the products to buy from a buyer """
    products = ProductToBuy.get_all_products(buyer_id)
    products_dict = list(map(lambda product_to_buy: product_to_buy.serialize(), products))
    return jsonify({
        "msg": "Petición exitosa",
        "products_to_buy" : products_dict
    }), 200



@app.route('/add-product', methods=['POST'])
def create_poduct_to_buy():
    """ Create a product to buy
        Request body example:
        {
            "buyer_id" : "2",
            "product_id" : "4",
            "quantity" : "1"
        }
     """
    request_body =  request.json
    product_to_buy = ProductToBuy.create(
        quantity = request_body['quantity'],
        buyer_id = request_body['buyer_id'],
        product_id = request_body['product_id']
    )
    if not isinstance(product_to_buy, ProductToBuy):
        return jsonify({
            "msg": "Ocurrió un error al crear el producto a comprar"
        }), 500
    product_to_buy.save()

    return jsonify({
        "msg" :  "Se creó la asociacion correctamente"
    }), 201

@app.route('/edit-product/<int:id>', methods=['PATCH'])
def edit_product_to_buy(id):
    """ Edit a existent product quantity.
        request body example
        {
            "quantity" : "new_quantity",
        }
    """
    request_body = request.json
    ProductToBuy.edit_quantity(id, request_body['quantity'])
    return jsonify({
        "msg" : "El producto fue actualizado satisfactoriamente"
    }), 200

@app.route('/product-to-buy/<int:id>', methods=['DELETE'])
def delete_product_to_buy(id):
    """ Delete a product to buy by id """
    ProductToBuy.delete_by_id(id)
    return jsonify({
        "msg": "Product eliminated successfully"
    }), 200

  
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
