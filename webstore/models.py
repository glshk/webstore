from flask_sqlalchemy import SQLAlchemy
from webstore import app
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter


db = SQLAlchemy(app)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(50), unique=True)
    orders = db.relationship('Order', backref='user')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users'))

    def __init__(self, first_name, last_name, email, phone):
        self.first_name=first_name
        self.last_name=last_name
        self.email=email
        self.phone=phone

    ## Method required by flask-login.
    def is_authenticated(self):
        return True

    ## Method required by flask-login.
    def is_active(self):
        return True

    ## Method required by flask-login.
    def is_anoymous(self):
        return False

    ## Method required by flask-login.
    def get_id(self):
        return self.id

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def __repr__(self):
        return 'User %s %s' % (self.first_name, self.last_name)



class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id, ondelete='CASCADE'))


class UserAuth(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False, unique=True)

    # user = db.relationship('User', uselist=False, foreign_keys=user_id)
    user = db.relationship('User', uselist=False, backref='user_auth')



class Order(db.Model):
    oid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    state = db.Column(db.Boolean)
    total_price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Order number %d by %r' % (self.oid, self.user)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.String)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    # price = db.Column(db.Integer)
    description = db.Column(db.String)

    brand_id = db.Column(db.Integer, db.ForeignKey(Brand.id))
    brand = db.relationship(Brand, backref='products')

    cat_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = db.relationship(Category, backref='products')

    image = db.Column(db.String(30))

    # def __init__(self, name, price, description):
    #     self.name = name
    #     self.price = price
    #     self.description = description


class OrderProducts(db.Model):
    order_id = db.Column(db.Integer, db.ForeignKey(Order.oid), primary_key=True)
    order = db.relationship(Order, backref='order_products')

    prod_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    products = db.relationship(Product, backref='order_products')

    size_id = db.Column(db.Integer, db.ForeignKey(Size.id), primary_key=True)
    sizes = db.relationship('Size', backref='order_products')

    amount = db.Column(db.Integer)

class InStock(db.Model):
    prod_id = db.Column(db.Integer, db.ForeignKey(Product.id), primary_key=True)
    products = db.relationship(Product, backref='instock')

    size_id = db.Column(db.Integer, db.ForeignKey(Size.id), primary_key=True)
    sizes = db.relationship(Size, backref='instock')

    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __init__(self, product, size, amount, price):
        self.products = product
        self.sizes = size
        self.amount = amount
        self.price = price


db_adapter = SQLAlchemyAdapter(db, User, UserAuthClass=UserAuth)
