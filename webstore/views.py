from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from flask_user import roles_required, UserMixin

from webstore import app
from webstore.models import *
from webstore.forms import LoginForm, SUpForm


# @app.route('/', methods=['POST', 'GET'])
# def index():
#     return 'Hello World!'

@app.route('/')
def index():
    # products = Product.query.filter(Product.id<=4)
    products = Product.query.join(InStock.products).filter(InStock.size_id==1).order_by(InStock.price).limit(4)
    prices = []
    for product in products:
        prices.append(InStock.query.join(InStock.products).filter(Product.id == product.id).first().price)
    return render_template('index1.html', products=products, prices=prices)

'''
def help_show_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('show_one.html', user=user)

@app.route('/user/<username>')
def user(username):
    # user = User.query.filter_by(username=username).first_or_404()
    # return render_template('show_one.html', user=user)
    return help_show_user(username)

@app.route('/orders_by_user/<username>')
def orders_by_user(username):
    orders = Order.query.join(Order.user).filter_by(username=username)
    return render_template('show_orders.html', orders=orders)

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('show_orders_1.html', orders=orders, pic='j1')

@app.route('/order/<id>')
def order(id):
    order = Order.query.filter_by(oid=id).first_or_404()
    return render_template('show_one.html', user=str(order.users.username))

@app.route('/users_by_order/<id>')
def users_by_order(id):
    users = User.query.join(User.orders).filter_by(oid=id)
    return render_template('show_orders.html', orders=users)

@app.route('/random')
def random():
    import random
    orders = Order.query.filter(Order.oid==random.randint(1,7))
    return render_template('show_orders.html', orders=orders)
'''



@app.route('/single')
def single():
    import random
    id = 3
    product = Product.query.join(InStock.products).filter(Product.id==id).first()
    sizes = Size.query.join(InStock.sizes).filter(InStock.prod_id==id).all()
    category = Category.query.join(Product.category).filter(Product.id==id).first()
    price = InStock.query.filter(InStock.prod_id==id).first().price
    return render_template('single.html', product=product, sizes=sizes, category=category, price=price)

@app.route('/single-<id>')
def single_id(id):
    product = Product.query.join(InStock.products).filter(Product.id == id).first()
    sizes = Size.query.join(InStock.sizes).filter(InStock.prod_id == id).all()
    category = Category.query.join(Product.category).filter(Product.id == id).first()
    price = InStock.query.filter(InStock.prod_id == id).first().price
    return render_template('single.html', product=product, sizes=sizes, category=category, price=price)




# @app.route('/products?<cat>', methods = ["GET", "POST"])
# def products_cat(cat):
#     brands = Brand.query.all()
#     products = Product.query.join(Product.category).filter(Product.cat_id==1)
#     return render_template('products.html', products=products, brands=brands)

@app.route('/products')
def products():
    products = Product.query.join(InStock.products).filter(InStock.size_id==1).all()
    prices = []
    for product in products:
        prices.append(InStock.query.join(InStock.products).filter(Product.id == product.id).first().price)
    return render_template('products.html', products=products, prices=prices)


@app.route('/products/<category>', methods=["GET", "POST"])
def products_cat(category):
    products = Product.query.join(Category.products).filter(Category.name==category)
    prices = []
    for product in products:
        prices.append(InStock.query.join(InStock.products).filter(Product.id==product.id).first().price)
    # return products
    return render_template('products.html', products=products, prices=prices)

@app.route('/products/sort', methods=["GET", "POST"])
def sorted():
    if request.form:
        brands=request.form.getlist('brand')
        # brands1 = [int(b) for b in brands]
        # brands1 =[]
        # for b in brands:
        #     brands1.append(b)
        # print(brands1)
        products = Product.query.join(Brand.products).filter(Brand.id.in_(set(brands))).all()
        prices = []
        for product in products:
            prices.append(InStock.query.join(InStock.products).filter(Product.id == product.id).first().price)
        return render_template('products.html', products=products, brands=brands, prices=prices)



# @app.route('/login')
# def login():
#     return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate():
        user = User.query.join(User.user_auth).filter_by(username=form.username.data,
                                    password=form.password.data).first()
        # user = User.query.join(AuthUser.user).filter_by(username='admin',
        #                             password='secret').first()
        if not user is None:
            login_user(user)
            flash('All fine')
            return redirect(url_for('index'))
        else:
            flash("Incorrect info!")
    # flashErrors(form.errors, flash)
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = SUpForm()
    if request.method == 'POST':
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, phone=form.phone.data)
        db.session.add(user)
        db.session.commit()

        user_role = UserRoles()
        user_role.user_id = user.id
        user_role.role_id = 1
        db.session.add(user_role)
        user_auth = UserAuth()
        user_auth.user_id=user.id
        user_auth.username = form.username.data
        user_auth.password = form.password.data
        db.session.add(user_auth)
        db.session.commit()

        flash("user " + form.username.data + " was added")
        return redirect(url_for('index'))
    else:
        flash("you are wrong")

    return render_template('register.html', form=form)




@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/admin')
@roles_required('admin')
def admin():
    return render_template('admin/admin.html')

@app.route('/admin/users', methods = ['GET', 'POST'])
def admin_users():
    pass

@app.route('/admin/products', methods = ['GET', 'POST'])
def admin_products():
    pass

@app.route('/admin/orders', methods = ['GET', 'POST'])
def admin_orders():
    pass
