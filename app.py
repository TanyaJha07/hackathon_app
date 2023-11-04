from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(120), nullable=False)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    vehicle_id = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding a new user'
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        users = User.query.all()
        for user in users:
            if user.username == username and user.password == password:
                return redirect(f'/user_dashboard/{user.id}')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/seller_signup', methods=['GET', 'POST'])
def seller_signup():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        mobile = request.form['mobile']
        seller = Seller(username=username, password=password, mobile=mobile)
        try:
            db.session.add(seller)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding a new seller'
    return render_template('seller_signup.html')

@app.route('/seller_login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        sellers = Seller.query.all()
        for seller in sellers:
            if seller.username == username and seller.password == password:
                return redirect(f'/seller_dashboard/{seller.id}')
        return redirect(url_for('seller_login'))
    return render_template('seller_login.html')

@app.route('/seller_dashboard/<int:seller_id>', methods=['GET', 'POST'])
def seller_dashboard(seller_id):
    seller = Seller.query.get(seller_id)
    if seller:
        if request.method == 'POST':
            name = request.form.get('name')
            vehicle_id = request.form.get('vehicle_id')
            latitude = float(request.form.get('latitude'))
            longitude = float(request.form.get('longitude'))
            
            # Create a new vehicle and associate it with the seller
            vehicle = Vehicle(name=name, vehicle_id=vehicle_id, latitude=latitude, longitude=longitude, seller_id=seller.id)
            db.session.add(vehicle)
            db.session.commit()
            
        # Retrieve associated vehicles for the seller
        vehicles = Vehicle.query.filter_by(seller_id=seller_id).all()
        return render_template('seller_dashboard.html', seller=seller, vehicles=vehicles)
    else:
        return "Seller not found"

@app.route('/user_dashboard/<int:user_id>')
def user_dashboard(user_id):
    return render_template('user_dashboard.html', user_id=user_id)

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    name = request.form.get('name')
    vehicle_id = request.form.get('vehicle_id')
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    seller_id = request.form.get('seller_id')  
    
    if request.form['action'] == 'Add Another Vehicle':
        with app.app_context():
            seller = Seller.query.get(seller_id)
            if seller:
                vehicle = Vehicle(name=name, vehicle_id=vehicle_id, latitude=latitude, longitude=longitude, seller_id=seller.id)
                db.session.add(vehicle)
                db.session.commit()
            else:
                return "Seller not found"
        return redirect(url_for('index'))
    if request.form['action'] == 'See Location of This Vehicle':
        return redirect(url_for('get_tracker_location', vehicle_id=vehicle_id))
    elif request.form['action'] == 'All Vehicle List':
        return redirect(url_for('vehicle_details'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name')
    seller_id = request.form.get('seller_id')
    if request.form['action'] == 'Add Another Category':
        with app.app_context():
            seller = Seller.query.get(seller_id)
            if seller:
                category = Category(name=name, seller_id=seller.id)
                db.session.add(category)
                db.session.commit()
            else:
                return "Seller not found"
        return redirect(url_for('seller_dashboard', seller_id=seller_id))
    elif request.form['action'] == 'All Category List':
        return redirect(url_for('category_details'))

@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    # Retrieve the category to be deleted
    category = Category.query.get(category_id)
    if category:
        # Get the seller_id before deleting the category
        seller_id = category.seller_id
        # Delete the category from the database
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('seller_dashboard', seller_id=seller_id))
    return "Category not found"

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
