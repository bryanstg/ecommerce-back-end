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
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    salt = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(240), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    # @property
    # def role(self):
    #     seller = Seller.query.filter_by(user_id == self.id).one_or_none()
    #     #if seller is None return "buyer"
    #     #return "seller"
    #     return "buyer"

    def __init__(self, username, email, password, is_active = True):
        """Constructor de clase Persona"""
        self.username = username
        self.email = email
        self.salt = os.urandom(16).hex()
        self.password = password
        self.is_active = is_active

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
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
    address = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    user = db.relationship("User", uselist=False)

    def __init__(self, id_number, first_name, last_name, address, user_id):
        """Constructor of Buyer's class"""
        self.id_number = id_number
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.user_id = user_id

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
            "address": self.address
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name):
        """Constructor of Category's class"""
        self.name = name

    def save(self):
        """ Save and commit a new Category """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Buyer %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Store(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    #categories = db.Column(db.Integer, db.ForeignKey('category.id'))
    #id_seller = db.Column(db.Integer, db.ForeignKey('seller.id'))
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
            "categories" : "self.categories",
            "seller_id" : "",
            "id_products" : {
                "products" :  [p.product.minialize() for p in self.products],
                "quantity": "",
                "categories" : "",
                "active": "",
                "deactivated": ""
            }
        }

class Product(db.Model, Crud):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240), unique=False, nullable=False)
    price = db.Column(db.String(80), unique=False, nullable=False)
    amount_available = db.Column(db.Integer, unique=False, nullable=False)
    active = db.Column(db.Boolean, unique=False, nullable=False)
    #categories_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))

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
            "categories" : "self.categories",
            "store_id" : self.store_id,
        }
    
    def minialize(self):
        """ Return a resumed serialize"""  
        return {
            "id" : self.id,
            "name" : self.name
        }  
