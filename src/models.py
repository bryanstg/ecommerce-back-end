from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Crud(object):
    @classmethod
    def create(cls, **kwargs):
        """ Create and return an instance """
        return cls(**kwargs)

    @classmethod
    def get_all(cls):
        """ Get all the elements from the table """
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        """ Return a specific instance from the table """
        return cls.query.get(id)

    @classmethod
    def delete_by_id(cls, id):
        """ Delete an instance from db by id """
        to_delete = cls.get_by_id(id)
        db.session.delete(to_delete)
        db.session.commit()


class User(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    salt = db.Column(db.String(40), nullable=False)
    hashed_password = db.Column(db.String(240), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    user_seller = db.relationship("Seller", backref="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    user_buyer = db.relationship("Buyer", backref="user", cascade="all, delete-orphan", passive_deletes=True, uselist=False)

    @property
    def role(self): 
        seller = Seller.query.filter_by(user_id = self.id).one_or_none()
        if seller is None:
            buyer = Buyer.query.filter_by(user_id = self.id).one_or_none()
            return "buyer"
        return "seller"

    def __init__(self, email, password, is_active = True):
        """ Constructor of an instance of User class"""
        self.email = email
        self.salt = os.urandom(16).hex()
        self.set_password(password)
        self.is_active = is_active

    def set_password(self, password):
        """ Create a hashed password """
        self.hashed_password = generate_password_hash(
            f"{password}{self.salt}"
        )

    def check_password(self, password):
        return check_password_hash(
            self.hashed_password, 
            f"{password}{self.salt}"
        )

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "user_seller" : self.user_seller.serialize() if self.user_seller is not None else None,
            "user_buyer" : self.user_buyer.serialize() if self.user_buyer is not None else None
            # do not serialize the password, its a security breach
        }

    def save(self):
        """ Save and commit a new User """
        db.session.add(self)
        db.session.commit()
        return self

class Buyer(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    id_number = db.Column(db.String(12), unique=True, nullable=False)
    cellphone_number = db.Column(db.String(30), unique=False, nullable=False)
    address = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    product_to_buy = db.relationship('ProductToBuy', backref='buyer')
    #shopping_car = db.relationship('ShoppingCar', backref='buyer')

    def save(self):
        """ Save and commit a new Buyer """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Buyer %r>' % self.first_name

    def serialize(self):
        return {
            "id": self.id,
            "id_number": self.id_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "cellphone_number" : self.cellphone_number,
            "address": self.address
        }

class Seller(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(250), nullable=False, unique=True)
    identification_number = db.Column(db.String(250), nullable=False, unique=True)
    cellphone_number = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)

    def save(self):
        """ Save and commit a new Seller """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Seller %r>' % self.company_name

    def serialize(self):
        return {
            "id": self.id,
            "company_nam": self.company_name,
            "identification_number" : self.identification_number,
            "cellphone_number" : self.cellphone_number,
            "user_id": self.user_id
        }

class Category(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    products = db.relationship('Product', backref='category')

    def save(self):
        """ Save and commit a new Category """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Categroy %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "products": [ p.minialize() for p  in self.products]
        }

    def minialize(self):
        return {
            "id" : self.id,
            "name" : self.name
        }

class Store(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    categories = db.Column(db.Integer, db.ForeignKey('category.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'))
    products = db.relationship('Product', backref='store')

    def save(self):
        """ Save and commit a new Store """
        db.session.add(self)
        db.session.commit()


    def __repr__(self):
        """ Return a representancion of the instance """
        return '<Store %r>' % self.name

    def serialize(self):
        """ Return a dictionary of the instance """
        return {
            "id" : self.id,
            "name" : self.name,
            "description" : self.description,
            "seller_id" : self.seller_id,
            "products" : {
                "quantity": len(self.products),
                "categories" : [c.category.minialize() for c in self.products],
            }
        }

class Product(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(240), nullable=False)
    price = db.Column(db.String(80), nullable=False)
    amount_available = db.Column(db.String(80), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    img_url = db.Column(db.String(360), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    product_to_buy = db.relationship('ProductToBuy', backref='product')

    @classmethod
    def get_by_store(cls, store_id):
        """ Get all the poducts in a store """
        return cls.query.filter_by(store_id = store_id)

    @classmethod
    def get_all_available(cls):
        """ get all the available products"""
        return cls.query.filter_by(active = True).all()

    
    def save(self):
        """ Save and commit a new Product """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """ Return a representancion of the instance """
        return '<Product %r>' % self.name

    def serialize(self):
        """ Return a dictionary of the instance """
        return {
            "id" : self.id,
            "name" : self.name,
            "description" : self.description,
            "price" : self.price,
            "amount_available" : self.amount_available,
            "active" : self.active,
            "category" : self.category.minialize(),
            "store_id" : self.store_id,
            "img_url" : self.img_url
        }
    
    def minialize(self):
        """ Return a resumed serialize"""  
        return {
            "id" : self.id,
            "name" : self.name
        }  

class ProductToBuy(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    quantity = db.Column(db.String(10), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    
    @classmethod
    def get_all_by_buyer_id(cls, buyer_id):
        """ Get all the products from a buyer id """
        return cls.query.filter_by(buyer_id = buyer_id).all()

    @classmethod
    def edit_quantity(cls, id, quantity):
        """Edit a product quantity column  """
        product = cls.get_by_id(id)
        product.quantity = quantity
        db.session.commit()

    def save(self):
        """ Save and commit a new ProductToBuy """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """ Return a representancion of the instance """
        return '<ProductToBuy %r>' % self.id

    def serialize(self):
        """ Return a dictionary of the instance """
        return {
            "id" : self.id,
            "product_id": self.product_id,
            "buyer_id": self.buyer_id,
            "quantity": self.quantity,
            "product" : product.serialize()
    