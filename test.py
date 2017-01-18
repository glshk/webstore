import os
import os.path as op
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from wtforms import validators

from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter

app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/test2'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



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
    # total_price = db.Column(db.Integer)
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


# Flask views
@app.route('/')
def index():
    return '<a href="/">Click me</a>'


def build_sample_db():

    import random
    import datetime

    db.reflect()
    db.drop_all()
    db.create_all()

    # Create sample Users
    first_names = [
        'Sophie', 'Mia',
        'Jacob', 'Thomas',
        'Benjamin', 'Stacey', 'Lucy'
    ]
    last_names = [
        'Taylor', 'Thomas',
        'Roberts', 'Wilson',
        'Ali', 'Mason', 'Davis'
    ]

    roles = [
        'buyer', 'admin'
    ]

    for i in range(len(roles)):
        role = Role()
        role.name = roles[i]
        db.session.add(role)

    user_list = []
    for i in range(len(first_names)):
        user = User(first_names[i], last_names[i], first_names[i].lower()+"@example.com", "0-123-4567-%d"%(i+1))
        user.roles.append(Role.query.filter_by(name='buyer').first())
        user_list.append(user)
        db.session.add(user)

        # password = Password()
        # password.username = user.username
        # password.password = 'password%d'%(i+1)
        # db.session.add(password)

    admin = User('Admin', 'Adminovich', 'admin@gmail.com', '0-050-5555-55')
    admin.roles.append(Role.query.filter_by(name='admin').first())
    db.session.add(admin)

    user_auth = UserAuth()
    user_auth.user_id = len(user_list)+1
    user_auth.username = 'admin'
    user_auth.password = 'secret'
    db.session.add(user_auth)

    brand_names = [
        'Levis', 'Mustang', 'Diesel', 'Armani', 'PepeJeans', 'Guess', 'Dockers'
    ]

    for i in range(len(brand_names)):
        brand = Brand()
        brand.name = brand_names[i]
        db.session.add(brand)


    category_names = [
        'men', 'women'
    ]

    for i in range(len(category_names)):
        category = Category()
        category.name = category_names[i]
        db.session.add(category)

    size_names = [
        'XS', 'S', 'M', 'L', 'XL'
    ]

    for i in range(len(size_names)):
        size = Size()
        size.name = size_names[i]
        db.session.add(size)

    product_names = [
        'Oliver Jeans', 'Jack Jeans', 'Isabella Jeans',
        'Charlie Jeans', 'Sophie Jeans', 'Mia Jeans', 'Harry Jeans', 'Amelia Jeans',
        'Golden Jeans', 'Smart Boy Jeans', 'Nevermind Jeans', 'Longlasting Jeans'
    ]

    cat_ids = [
        1, 1, 2, 1, 2, 2, 1, 2, 2, 1, 1, 2
    ]

    for i in range(len(product_names)):
        product = Product()
        product.name = product_names[i]
        product.brand = Brand.query.filter(Brand.id==random.randint(1, len(brand_names))).first()
        product.category = Category.query.filter(Category.id==cat_ids[i]).first()
        # product.price = 50*random.randint(3,8)
        product.description = "The best jeans you could ever find"
        product.image = "j%d" % (i+1)
        db.session.add(product)

    for i in range(len(product_names)):
        price = 50*random.randint(3,8)
        for j in range (len(size_names)):
            instock = InStock(Product.query.filter(Product.id==i+1).first(), Size.query.filter(Size.id==j+1).first(), 10*random.randint(0, 3), price)
            # instock.products.append(Product.query.filter(Product.id==i+1).first())
            # instock.sizes.append(Size.query.filter(Size.id==j+1).first())
            # # instock.prod_id = i+1
            # # instock.size_id = j+1
            # instock.amount = 10*random.randint(0, 3)
            # instock.price = price
        # random.randint(1, 300)
            db.session.add(instock)

    order_list = []
    for user in user_list:
        order = Order()
        order.user_id = user.id
        tmp = int(1000*random.random())  # random number between 0 and 1000:
        order.date = datetime.datetime.now() - datetime.timedelta(days=tmp)
        order.state = random.choice([True, False])
        order_list.append(order)
        db.session.add(order)

        user_auth = UserAuth()
        user_auth.user_id=user.id
        user_auth.username = user.first_name.lower()
        user_auth.password = 'password%d' % user.id
        db.session.add(user_auth)

    for order in order_list:

        i = random.randint(1, 3)
        for j in range(1, i+1):
            orderproduct = OrderProducts()
            orderproduct.order = order
            orderproduct.prod_id = i*3+j
            orderproduct.size_id = j+1
            k = random.randint(1,5)
            orderproduct.amount = k
            price = InStock.query.filter(InStock.prod_id == i*3+j).filter(InStock.size_id == j+1).first().price
            db.session.add(orderproduct)

    db.session.commit()
    return

if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    '''
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
        '''
    build_sample_db()
    # Start app
    # app.run(debug=True)
    #app.run()