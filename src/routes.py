from flask import current_app as app, render_template, request, redirect, url_for, flash, session
from functools import wraps
import datetime
import re
from . import db
from . import models

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.')
            return redirect(url_for('login'))
        user = models.User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You are not authorized to view this page.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner

@app.route('/admin')
@admin_required
def admin():
    user = models.User.query.get(session['user_id'])
    return render_template('admin.html', user=user, categories=models.Category.query.all())

@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user=models.User.query.get(session['user_id']))

@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    user = models.User.query.get(session['user_id'])
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    if username == '' or password == '' or cpassword == '':
        flash('Username or password cannot be empty.')
        return redirect(url_for('profile'))
    if not user.check_password(cpassword):
        flash('Incorrect password.')
        return redirect(url_for('profile'))
    if models.User.query.filter_by(username=username).first() and username != user.username:
        flash('User with this username already exists.')
        return redirect(url_for('profile'))
    user.username = username
    user.name = name
    if password:
        user.password = password
    db.session.commit()
    flash('Profile updated successfully.')
    return redirect(url_for('profile'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = models.User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    session['user_id'] = user.id
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    if not username or not password:
        flash('Username and password are required.')
        return redirect(url_for('register'))
    if models.User.query.filter_by(username=username).first():
        flash('Username already exists.')
        return redirect(url_for('register'))
    user = models.User(username=username, password=password, name=name)
    db.session.add(user)
    db.session.commit()
    flash('Successfully registered.')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/category/add')
@admin_required
def add_category():
    return render_template('category/add.html', user=models.User.query.get(session['user_id']))

@app.route('/category/add', methods=['POST'])
@admin_required
def add_category_post():
    name = request.form.get('name')
    if not name:
        flash('Name is required.')
        return redirect(url_for('add_category'))
    category = models.Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash('Category added.')
    return redirect(url_for('admin'))

@app.route('/category/<int:id>/show')
@admin_required
def show_category(id):
    return render_template('category/show.html', user=models.User.query.get(session['user_id']), category=models.Category.query.get(id))

@app.route('/product/add')
@admin_required
def add_product():
    category_id = request.args.get('category_id', -1, type=int)
    return render_template('product/add.html', 
                           user=models.User.query.get(session['user_id']), 
                           category_id=category_id,
                           categories=models.Category.query.all(),
                           nowstring=datetime.datetime.now().strftime("%Y-%m-%d"))

@app.route('/product/add', methods=['POST'])
@admin_required
def add_product_post():
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    category_id = request.form.get('category')
    man_date = request.form.get('manufacture_date')
    
    if not all([name, quantity, price, category_id, man_date]):
        flash('All fields are required.')
        return redirect(url_for('add_product'))
        
    product = models.Product(
        name=name, 
        quantity=int(quantity), 
        price=float(price), 
        category_id=int(category_id), 
        man_date=datetime.datetime.strptime(man_date, '%Y-%m-%d')
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added.')
    return redirect(url_for('admin'))

@app.route('/')
@auth_required
def index():
    user = models.User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    return render_template('index.html', user=user, categories=models.Category.query.all(), parameters={})

@app.route('/cart/<int:product_id>/add', methods=['POST'])
@auth_required
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)
    product = models.Product.query.get_or_404(product_id)
    if product.quantity < quantity:
        flash('Not enough stock.')
        return redirect(url_for('index'))
    cart_item = models.Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.Cart(user_id=session['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart.')
    return redirect(url_for('index'))

@app.route('/cart')
@auth_required
def cart():
    carts = models.Cart.query.filter_by(user_id=session['user_id']).all()
    total = sum([c.product.price * c.quantity for c in carts])
    return render_template('cart.html', user=models.User.query.get(session['user_id']), carts=carts, total=total)

@app.route('/cart/place_order', methods=['POST'])
@auth_required
def place_order():
    cart_items = models.Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Cart is empty.')
        return redirect(url_for('cart'))
    transaction = models.Transaction(user_id=session['user_id'], total=0)
    db.session.add(transaction)
    for item in cart_items:
        item.product.quantity -= item.quantity
        order = models.Order(transaction=transaction, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(order)
        transaction.total += item.product.price * item.quantity
        db.session.delete(item)
    db.session.commit()
    flash('Order placed.')
    return redirect(url_for('orders'))

@app.route('/orders')
@auth_required
def orders():
    transactions = models.Transaction.query.filter_by(user_id=session['user_id']).order_by(models.Transaction.datetime.desc()).all()
    return render_template('orders.html', user=models.User.query.get(session['user_id']), transactions=transactions)
