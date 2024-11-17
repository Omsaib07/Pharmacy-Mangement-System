from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask import Flask, render_template, request, session, redirect, flash, url_for
from datetime import datetime
# Load configuration parameters
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# Initialize Flask app  
app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Configure SQLAlchemy with MySQL Connector
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Omsai7%40sql@localhost/Medical'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
# Initialize the database
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    # Relationship
    medicines = db.relationship('Medicines', backref='user', lazy=True)
    posts = db.relationship('Posts', backref='user', lazy=True)
    logs = db.relationship('Logs', backref='user', lazy=True)

class Medicines(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)  # Changed from sno to id
    amount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    medicines = db.Column(db.String(100))
    products = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False)
    mid = db.Column(db.String(100), nullable=False)
    medicine_quantity = db.Column(db.Integer, default=0)
    product_quantity = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(12), nullable=False, default=datetime.now().strftime("%Y-%m-%d"))
    status = db.Column(db.String(20), default='pending')
    total_price = db.Column(db.Float, nullable=False)

class Posts(db.Model):
    __tablename__ = 'posts'
    mid = db.Column(db.Integer, primary_key=True)
    medical_name = db.Column(db.String(80), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Addmp(db.Model):
    __tablename__ = 'addmp'
    sno = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    medicine_price = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    

class Addpd(db.Model):
    __tablename__ = 'addpd'
    sno = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product_price = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

 # import your models accordingly
with app.app_context():
    db.create_all()

@app.route("/")

def hello():
    # If user is logged in, redirect to appropriate dashboard
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashbord'))
        return redirect(url_for('view_medicines'))
    return render_template('index.html', params=params)


@app.route("/")
def home():
    return redirect(url_for('index.html'))

# Add this temporarily to debug

@app.route("/view_medicines")
def view_medicines():
    available_medicines = Addmp.query.filter(Addmp.quantity > 0).all()
    available_products = Addpd.query.filter(Addpd.quantity > 0).all()
    
    print("Products:", available_products)  # Debug print
    
    return render_template('view_medicines.html', 
                         medicines=available_medicines,
                         products=available_products,  # Change posts to products
                         params=params)
@app.route("/dashbord")
def dashbord():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Posts.query.all()
    return render_template("dashbord.html", params=params, posts=posts)

@app.route("/search", methods=['GET', 'POST'])  # Added methods=['GET', 'POST']
def search():
    # First check if user is logged in and is admin
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    if request.method == 'POST':
        name = request.form.get('search', '').strip()  # Remove whitespace
        
        if not name:
            flash("Please enter a search term.", "warning")
            return render_template('search.html', params=params)
            
        # Case-insensitive search using LIKE
        posts = Addmp.query.filter(Addmp.medicine.ilike(f'%{name}%')).all()
        products = Addpd.query.filter(Addpd.product.ilike(f'%{name}%')).all()
        
        total_results = len(posts) + len(products)
        
        if total_results > 0:
            flash(f"Found {total_results} matching items.", "success")
            return render_template('search.html', 
                                params=params,
                                medicines=posts,
                                products=products,
                                search_term=name)
        else:
            flash("No matching items found.", "danger")
            
    return render_template('search.html', params=params)

@app.route("/details", methods=['GET', 'POST'])
def details():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Logs.query.all()
    return render_template('details.html', params=params, posts=posts)
from sqlalchemy.exc import SQLAlchemyError

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(e):
    # Check for the specific error message from the trigger
    if 'Medical ID must be a positive number' in str(e):
        flash('Medical ID must be a positive number', 'danger')
    else:
        flash('An unexpected error occurred. Please try again.', 'danger')
    return redirect(url_for('insert'))

@app.route("/insert", methods=['GET', 'POST'])
def insert():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    if request.method == 'POST':
        mid = request.form.get('mid')
        medical_name = request.form.get('medical_name')
        owner_name = request.form.get('owner_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        user_id = session['user_id']  # Add user_id to the post
        
        try:
            push = Posts(mid=mid, medical_name=medical_name, owner_name=owner_name, 
                         phone_no=phone_no, address=address, user_id=user_id)
            db.session.add(push)
            db.session.commit()
            flash("Thanks for submitting your details", "success")
        except SQLAlchemyError as e:
            db.session.rollback()  # Roll back any changes due to the error
            handle_sqlalchemy_error(e)  # Call the custom error handler

        return redirect(url_for('insert'))
    
    return render_template('insert.html', params=params)


@app.route("/addmp", methods=['GET', 'POST'])
def addmp():
    if request.method == 'POST':
        newmedicine = request.form.get('medicine')
        quantity = request.form.get('quantity', type=int)
        price = request.form.get('price', type=float)  # Get the price from the form

        existing_medicine = Addmp.query.filter_by(medicine=newmedicine).first()

        if existing_medicine:
            # Increment quantity and update price
            existing_medicine.quantity += quantity
            existing_medicine.medicine_price = price  # Update the price
            flash(f"Updated quantity and price for {newmedicine}.", "primary")
        else:
            # Create a new entry
            push = Addmp(medicine=newmedicine, quantity=quantity, medicine_price=price)
            db.session.add(push)
            flash(f"Added new medicine: {newmedicine} with price {price}.", "primary")

        db.session.commit()
    return render_template('search.html', params=params)

@app.route("/addpd", methods=['GET', 'POST'])
def addpd():
    if request.method == 'POST':
        newproduct = request.form.get('product')
        quantity = request.form.get('quantity', type=int)
        price = request.form.get('price', type=float)  # Get the price from the form

        existing_product = Addpd.query.filter_by(product=newproduct).first()

        if existing_product:
            # Increment quantity and update price
            existing_product.quantity += quantity
            existing_product.product_price = price  # Update the price
            flash(f"Updated quantity and price for {newproduct}.", "primary")
        else:
            # Create a new entry
            push = Addpd(product=newproduct, quantity=quantity, product_price=price)
            db.session.add(push)
            flash(f"Added new product: {newproduct} with price {price}.", "primary")

        db.session.commit()
    return render_template('search.html', params=params)

@app.route("/list", methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Medicines.query.all()
    return render_template('post.html', params=params, posts=posts)

@app.route("/items", methods=['GET', 'POST'])
def items():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Addmp.query.all()
    return render_template('items.html', params=params, posts=posts)

@app.route("/items2", methods=['GET', 'POST'])
def items2():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Addpd.query.all()
    return render_template('items2.html', params=params, posts=posts)

@app.route("/sp", methods=['GET', 'POST'])
def sp():
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    posts = Medicines.query.all()
    return render_template('store.html', params=params, posts=posts)

@app.route("/logout",methods=['POST','GET'])
def logout():
    session.clear()
    flash("You have been logged out", "primary")
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and user.password == password:
            # Store user information in session
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            
            flash("Logged in successfully", "success")
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('dashbord'))
            return redirect(url_for('user_medicines'))
            
        flash("Invalid username or password", "danger")
    return render_template('login.html', params=params)

@app.route("/edit/<string:mid>", methods=['GET', 'POST'])
def edit(mid):
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    if request.method == 'POST':
        medical_name = request.form.get('medical_name')
        owner_name = request.form.get('owner_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        
        post = Posts.query.filter_by(mid=mid).first()
        if post:
            post.medical_name = medical_name
            post.owner_name = owner_name
            post.phone_no = phone_no
            post.address = address
            db.session.commit()
            flash("Data Updated Successfully", "success")
            return redirect(url_for('dashbord'))
    
    post = Posts.query.filter_by(mid=mid).first()
    return render_template('edit.html', params=params, post=post)


#         if user is logged in
#delete
from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify

@app.route("/verify_mid/<mid>")
def verify_mid(mid):
    try:
        medical = Posts.query.filter_by(mid=mid).first()
        if medical:
            return jsonify({
                'exists': True,
                'name': medical.medical_name
            })
        return jsonify({
            'exists': False,
            'name': None
        })
    except Exception as e:
        print(f"Error in verify_mid: {str(e)}")
        return jsonify({
            'exists': False,
            'name': None,
            'error': str(e)
        }), 500
    

@app.route("/delete/<string:mid>", methods=['GET', 'POST'])
def delete(mid):
    if 'user_id' not in session:
        flash("Please log in", "danger")
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash("Access denied. Admin privileges required.", "danger")
        return redirect(url_for('user_medicines'))
    
    post = Posts.query.filter_by(mid=mid).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "warning")
    
    return redirect(url_for('dashbord'))

# Add this route to your Flask application
@app.route("/deletemp/<int:id>", methods=['GET', 'POST'])
def delete_order(id):
    try:
        print(f"Delete order initiated for ID: {id}")  # Debug log
        
        # Check if user is logged in and has the correct role
        if 'user_id' not in session:
            print("User not in session")  # Debug log
            flash("Please login to delete orders", "danger")
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            print(f"Invalid role: {session.get('role')}")  # Debug log
            flash("Unauthorized access. Admin privileges required.", "danger")
            return redirect(url_for('login'))
        
        # Find the order to be deleted
        order = Medicines.query.filter_by(id=id).first()
        print(f"Order found: {order}")  # Debug log
        
        if not order:
            print(f"No order found with ID: {id}")  # Debug log
            flash("Order not found", "danger")
            return redirect(url_for('post'))  # Changed to 'post' instead of 'orders_page'
        
        # Restore quantities to inventory before deleting
        if order.medicine_quantity > 0 and order.medicines != "No medicine ordered":
            medicine = Addmp.query.filter_by(medicine=order.medicines).first()
            if medicine:
                print(f"Restoring medicine quantity: {order.medicine_quantity} to {medicine.medicine}")  # Debug log
                medicine.quantity += order.medicine_quantity
                db.session.commit()
                print("Medicine quantity restored")  # Debug log
        
        if order.product_quantity > 0 and order.products != "No product ordered":
            product = Addpd.query.filter_by(product=order.products).first()
            if product:
                print(f"Restoring product quantity: {order.product_quantity} to {product.product}")  # Debug log
                product.quantity += order.product_quantity
                db.session.commit()
                print("Product quantity restored")  # Debug log
        
        # Create log entry
        log_entry = Logs(
            mid=order.mid,
            action=f"Deleted order - Medicine: {order.medicines} (Qty: {order.medicine_quantity}), "
                  f"Product: {order.products} (Qty: {order.product_quantity})",
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=session['user_id']  # Added user_id to log entry
        )
        
        # Add log entry and delete order
        try:
            db.session.add(log_entry)
            print("Log entry added")  # Debug log
            
            db.session.delete(order)
            print("Order marked for deletion")  # Debug log
            
            db.session.commit()
            print("Changes committed successfully")  # Debug log
            
            flash("Order deleted successfully and inventory restored", "success")
        except Exception as inner_e:
            print(f"Error during final database operations: {str(inner_e)}")  # Debug log
            db.session.rollback()
            raise  # Re-raise the exception to be caught by outer try-except
            
    except Exception as e:
        print(f"Error deleting order: {str(e)}")  # Debug log
        db.session.rollback()
        flash("Error occurred while deleting the order", "danger")
    
    return redirect(url_for('post'))  # Changed to 'post' instead of 'orders_page'

from datetime import datetime
from flask import Flask, render_template, request, session, redirect, flash, url_for

@app.route("/view_medicals")
def view_medicals():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("Please log in to view medical stores", "danger")
        return redirect(url_for('login'))
    
    try:
        # Fetch all medical stores from Posts table
        medical_stores = Posts.query.all()
        
        return render_template(
            'view_medicals.html',
            params=params,
            medical_stores=medical_stores
        )
    except Exception as e:
        print(f"Error: {str(e)}")  # For debugging
        flash("An error occurred while fetching medical stores.", "danger")
        return redirect(url_for('user_medicines'))
    

# Update the `medicine` route
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import event

from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

@app.route("/medicines", methods=['GET', 'POST'])
def medicine():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("Please log in to place an order.", "danger")
            return redirect(url_for('login'))

        user_id = session.get('user_id')
        
        form_data = {
            'mid': request.form.get('mid'),
            'name': request.form.get('name'),
            'selected_medicine': request.form.get('medicines'),
            'selected_product': request.form.get('products'),
            'medicine_quantity': request.form.get('medicine_quantity', '0'),
            'product_quantity': request.form.get('product_quantity', '0'),
            'email': request.form.get('email')
        }
        
        print("Processed form data:", form_data)

        try:
            # Start database transaction
            db.session.begin()
            
            # Validate Medical ID
            medical = Posts.query.filter_by(mid=form_data['mid']).first()
            if not medical:
                flash("Invalid Medical ID. Please register your medical store first.", "danger")
                return redirect(url_for('medicine'))

            medicine = None
            product = None
            medicine_quantity = 0
            product_quantity = 0
            total_price = 0

            # Process medicine order with direct database update
            if form_data['selected_medicine'] and form_data['medicine_quantity']:
                try:
                    medicine_quantity = int(form_data['medicine_quantity'])
                    if medicine_quantity <= 0:
                        raise ValueError("Medicine quantity must be greater than 0")

                    # Lock the medicine record for update
                    medicine = db.session.query(Addmp).filter_by(
                        sno=form_data['selected_medicine']
                    ).with_for_update().first()

                    if not medicine:
                        raise ValueError("Selected medicine not found")

                    if medicine.quantity < medicine_quantity:
                        raise ValueError(f"Insufficient medicine stock. Available: {medicine.quantity}")

                    # Calculate price
                    medicine_price = float(medicine.medicine_price)
                    total_price += medicine_quantity * medicine_price
                    print(f"Medicine price calculation: {medicine_quantity} x ₹{medicine_price} = ₹{medicine_quantity * medicine_price}")

                    # Update medicine quantity directly in database
                    new_quantity = medicine.quantity - medicine_quantity
                    db.session.execute(
                        "UPDATE addmp SET quantity = :new_quantity WHERE sno = :sno",
                        {"new_quantity": new_quantity, "sno": medicine.sno}
                    )

                except ValueError as e:
                    db.session.rollback()
                    flash(str(e), "danger")
                    return redirect(url_for('medicine'))

            # Process product order with direct database update
            if form_data['selected_product'] and form_data['product_quantity']:
                try:
                    product_quantity = int(form_data['product_quantity'])
                    if product_quantity <= 0:
                        raise ValueError("Product quantity must be greater than 0")

                    # Lock the product record for update
                    product = db.session.query(Addpd).filter_by(
                        sno=form_data['selected_product']
                    ).with_for_update().first()

                    if not product:
                        raise ValueError("Selected product not found")

                    if product.quantity < product_quantity:
                        raise ValueError(f"Insufficient product stock. Available: {product.quantity}")

                    # Calculate price
                    product_price = float(product.product_price)
                    total_price += product_quantity * product_price
                    print(f"Product price calculation: {product_quantity} x ₹{product_price} = ₹{product_quantity * product_price}")

                    # Update product quantity directly in database
                    new_quantity = product.quantity - product_quantity
                    db.session.execute(
                        "UPDATE addpd SET quantity = :new_quantity WHERE sno = :sno",
                        {"new_quantity": new_quantity, "sno": product.sno}
                    )

                except ValueError as e:
                    db.session.rollback()
                    flash(str(e), "danger")
                    return redirect(url_for('medicine'))

            if not medicine and not product:
                flash("Please select at least one medicine or product to order.", "danger")
                return redirect(url_for('medicine'))

            total_price = round(total_price, 2)
            print(f"Final total price: ₹{total_price}")

            try:
                # Create order entry
                new_order = Medicines(
                    mid=form_data['mid'],
                    name=form_data['name'],
                    medicines=medicine.medicine if medicine else None,
                    products=product.product if product else None,
                    email=form_data['email'],
                    total_price=total_price,
                    medicine_quantity=medicine_quantity if medicine else 0,
                    product_quantity=product_quantity if product else 0,
                    user_id=user_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    status="pending",
                    amount=medicine_quantity + product_quantity
                )
                db.session.add(new_order)

                # Create log entry
                log_entry = Logs(
                    mid=form_data['mid'],
                    action=f"Order placed - Total: ₹{total_price} | "
                          f"Medicine: {medicine.medicine if medicine else 'None'} (Qty: {medicine_quantity if medicine else 0}) | "
                          f"Product: {product.product if product else 'None'} (Qty: {product_quantity if product else 0})",
                    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user_id=user_id
                )
                db.session.add(log_entry)

                # Commit all changes
                db.session.commit()
                flash(f"Order placed successfully! Total price: ₹{total_price}", "success")
                return redirect(url_for('medicine'))

            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Database error: {str(e)}")
                flash("An error occurred while processing your order. Please try again.", "danger")
                return redirect(url_for('medicine'))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            flash("An unexpected error occurred. Please try again.", "danger")
            return redirect(url_for('medicine'))

    # GET request handling
    medicines = Addmp.query.filter(Addmp.quantity > 0).all()
    products = Addpd.query.filter(Addpd.quantity > 0).all()
    all_medicines = Addmp.query.all()
    all_products = Addpd.query.all()

    return render_template(
        'medicine.html',
        params=params,
        medicines=medicines,
        products=products,
        all_medicines=all_medicines,
        all_products=all_products
    )


# Update the `user_medicines` route

# Update the `user_medicines` route
@app.route("/user_medicines", methods=['GET', 'POST'])
def user_medicines():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("Please log in to place an order.", "danger")
            return redirect(url_for('login'))

        user_id = session.get('user_id')
        
        form_data = {
            'mid': request.form.get('mid'),
            'name': request.form.get('name'),
            'selected_medicine': request.form.get('medicines'),
            'selected_product': request.form.get('products'),
            'medicine_quantity': request.form.get('medicine_quantity', '0'),
            'product_quantity': request.form.get('product_quantity', '0'),
            'email': request.form.get('email')
        }
        
        print("Processed form data:", form_data)

        try:
            # Start database transaction
            db.session.begin()
            
            # Validate Medical ID
            medical = Posts.query.filter_by(mid=form_data['mid']).first()
            if not medical:
                flash("Invalid Medical ID. Please register your medical store first.", "danger")
                return redirect(url_for('user_medicines'))

            # Verify the name matches the registered medical store
            if medical.medical_name.lower() != form_data['name'].lower():
                flash("Medical store name does not match the registered name for this ID.", "danger")
                return redirect(url_for('user_medicines'))

            medicine = None
            product = None
            medicine_quantity = 0
            product_quantity = 0
            total_price = 0

            # Process medicine order with direct database update
            if form_data['selected_medicine'] and form_data['medicine_quantity']:
                try:
                    medicine_quantity = int(form_data['medicine_quantity'])
                    if medicine_quantity <= 0:
                        raise ValueError("Medicine quantity must be greater than 0")

                    # Lock the medicine record for update
                    medicine = db.session.query(Addmp).filter_by(
                        sno=form_data['selected_medicine']
                    ).with_for_update().first()

                    if not medicine:
                        raise ValueError("Selected medicine not found")

                    if medicine.quantity < medicine_quantity:
                        raise ValueError(f"Insufficient medicine stock. Available: {medicine.quantity}")

                    # Calculate price
                    medicine_price = float(medicine.medicine_price)
                    total_price += medicine_quantity * medicine_price
                    print(f"Medicine price calculation: {medicine_quantity} x ₹{medicine_price} = ₹{medicine_quantity * medicine_price}")

                    # Update medicine quantity directly in database
                    new_quantity = medicine.quantity - medicine_quantity
                    db.session.execute(
                        "UPDATE addmp SET quantity = :new_quantity WHERE sno = :sno",
                        {"new_quantity": new_quantity, "sno": medicine.sno}
                    )

                except ValueError as e:
                    db.session.rollback()
                    flash(str(e), "danger")
                    return redirect(url_for('user_medicines'))

            # Process product order with direct database update
            if form_data['selected_product'] and form_data['product_quantity']:
                try:
                    product_quantity = int(form_data['product_quantity'])
                    if product_quantity <= 0:
                        raise ValueError("Product quantity must be greater than 0")

                    # Lock the product record for update
                    product = db.session.query(Addpd).filter_by(
                        sno=form_data['selected_product']
                    ).with_for_update().first()

                    if not product:
                        raise ValueError("Selected product not found")

                    if product.quantity < product_quantity:
                        raise ValueError(f"Insufficient product stock. Available: {product.quantity}")

                    # Calculate price
                    product_price = float(product.product_price)
                    total_price += product_quantity * product_price
                    print(f"Product price calculation: {product_quantity} x ₹{product_price} = ₹{product_quantity * product_price}")

                    # Update product quantity directly in database
                    new_quantity = product.quantity - product_quantity
                    db.session.execute(
                        "UPDATE addpd SET quantity = :new_quantity WHERE sno = :sno",
                        {"new_quantity": new_quantity, "sno": product.sno}
                    )

                except ValueError as e:
                    db.session.rollback()
                    flash(str(e), "danger")
                    return redirect(url_for('user_medicines'))

            if not medicine and not product:
                flash("Please select at least one medicine or product to order.", "danger")
                return redirect(url_for('user_medicines'))

            total_price = round(total_price, 2)
            print(f"Final total price: ₹{total_price}")

            try:
                # Create order entry
                new_request = Medicines(
                    mid=form_data['mid'],
                    name=form_data['name'],
                    medicines=medicine.medicine if medicine else None,
                    products=product.product if product else None,
                    email=form_data['email'],
                    total_price=total_price,
                    medicine_quantity=medicine_quantity if medicine else 0,
                    product_quantity=product_quantity if product else 0,
                    user_id=user_id,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    status="pending",
                    amount=medicine_quantity + product_quantity
                )
                db.session.add(new_request)

                # Create log entry
                log_entry = Logs(
                    mid=form_data['mid'],
                    action=f"User requested - Total: ₹{total_price} | "
                          f"Medicine: {medicine.medicine if medicine else 'None'} (Qty: {medicine_quantity if medicine else 0}) | "
                          f"Product: {product.product if product else 'None'} (Qty: {product_quantity if product else 0})",
                    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user_id=user_id
                )
                db.session.add(log_entry)

                # Commit all changes
                db.session.commit()
                flash(f"Your request has been submitted successfully! Total price: ₹{total_price}", "success")
                return redirect(url_for('user_medicines'))

            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Database error: {str(e)}")
                flash("An error occurred while processing your request. Please try again.", "danger")
                return redirect(url_for('user_medicines'))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            flash("An unexpected error occurred. Please try again.", "danger")
            return redirect(url_for('user_medicines'))

    # GET request handling
    medicines = Addmp.query.filter(Addmp.quantity > 0).all()
    products = Addpd.query.filter(Addpd.quantity > 0).all()
    all_medicines = Addmp.query.all()
    all_products = Addpd.query.all()

    return render_template(
        'user_medicines.html',
        params=params,
        medicines=medicines,
        products=products,
        all_medicines=all_medicines,
        all_products=all_products
    )
app.run(host='0.0.0.0',debug=True, port = 5001)