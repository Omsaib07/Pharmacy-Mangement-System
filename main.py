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

class Addpd(db.Model):
    __tablename__ = 'addpd'
    sno = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

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
        
        push = Posts(mid=mid, medical_name=medical_name, owner_name=owner_name, 
                    phone_no=phone_no, address=address, user_id=user_id)
        db.session.add(push)
        db.session.commit()
        
        flash("Thanks for submitting your details", "success")
        return redirect(url_for('insert'))
    
    return render_template('insert.html', params=params)


@app.route("/addmp", methods=['GET', 'POST'])
def addmp():
    if request.method == 'POST':
        '''ADD ENTRY TO THE DATABASE'''
        newmedicine = request.form.get('medicine')
        quantity = request.form.get('quantity', type=int)  # Get the quantity from the form

        existing_medicine = Addmp.query.filter_by(medicine=newmedicine).first()

        if existing_medicine:
            # Increment the quantity if the medicine already exists
            existing_medicine.quantity += quantity
            flash(f"Updated quantity for {newmedicine}.", "primary")
        else:
            # Create a new entry
            push = Addmp(medicine=newmedicine, quantity=quantity)
            db.session.add(push)
            flash(f"Added new medicine: {newmedicine}.", "primary")

        db.session.commit()
    return render_template('search.html', params=params)

@app.route("/addpd", methods=['GET', 'POST'])
def addpd():
    if request.method == 'POST':
        '''ADD ENTRY TO THE DATABASE'''
        newproduct = request.form.get('product')
        quantity = request.form.get('quantity', type=int)  # Get the quantity from the form

        existing_product = Addpd.query.filter_by(product=newproduct).first()

        if existing_product:
            # Increment the quantity if the product already exists
            existing_product.quantity += quantity
            flash(f"Updated quantity for {newproduct}.", "primary")
        else:
            # Create a new entry
            push = Addpd(product=newproduct, quantity=quantity)
            db.session.add(push)
            flash(f"Added new product: {newproduct}.", "primary")

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
@app.route("/medicines", methods=['GET', 'POST'])
def medicine():
    if request.method == 'POST':
        # Retrieve form data
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
        print("Required fields check:", {
            'mid': bool(form_data['mid']),
            'name': bool(form_data['name']),
            'email': bool(form_data['email'])
        })
        try:
            # Check if the medical ID exists in the Posts table
            medical = Posts.query.filter_by(mid=form_data['mid']).first()
            if not medical:
                flash("Invalid Medical ID. Please register your medical store first.", "danger")
                return redirect(url_for('medicine'))

            # Basic validation for required fields
            if not all([form_data['mid'], form_data['name'], form_data['email']]):
                flash("Please fill in all required fields (ID, Name, and Email).", "danger")
                return redirect(url_for('medicine'))

            # Verify the name matches the registered medical store
            if medical.medical_name.lower() != form_data['name'].lower():
                flash("Medical store name does not match the registered name for this ID.", "danger")
                return redirect(url_for('medicine'))
            
             # Modified validation for required fields
            missing_fields = []
            if not form_data['mid']:
                missing_fields.append("Medical ID")
            if not form_data['name']:
                missing_fields.append("Name")
            if not form_data['email']:
                missing_fields.append("Email")

            if missing_fields:
                flash(f"Please fill in the following required fields: {', '.join(missing_fields)}", "danger")
                return redirect(url_for('medicine'))

            medicine = None
            product = None
            medicine_quantity = 0
            product_quantity = 0
            total_amount = 0
            uesr_id=0

            # Process medicine order if selected
            if form_data['selected_medicine'] and form_data['medicine_quantity']:
                try:
                    medicine_quantity = int(form_data['medicine_quantity'])
                    if medicine_quantity <= 0:
                        flash("Medicine quantity must be greater than 0.", "danger")
                        return redirect(url_for('medicine'))
                    
                    medicine = Addmp.query.filter_by(sno=form_data['selected_medicine']).first()
                    if not medicine:
                        flash("Selected medicine not found.", "danger")
                        return redirect(url_for('medicine'))
                    
                    if medicine.quantity < medicine_quantity:
                        flash(f"Insufficient medicine stock. Available: {medicine.quantity}", "danger")
                        return redirect(url_for('medicine'))
                except ValueError:
                    flash("Please enter a valid medicine quantity.", "danger")
                    return redirect(url_for('medicine'))

            # Process product order if selected
            if form_data['selected_product'] and form_data['product_quantity']:
                try:
                    product_quantity = int(form_data['product_quantity'])
                    if product_quantity <= 0:
                        flash("Product quantity must be greater than 0.", "danger")
                        return redirect(url_for('medicine'))
                    
                    product = Addpd.query.filter_by(sno=form_data['selected_product']).first()
                    if not product:
                        flash("Selected product not found.", "danger")
                        return redirect(url_for('medicine'))
                    
                    if product.quantity < product_quantity:
                        flash(f"Insufficient product stock. Available: {product.quantity}", "danger")
                        return redirect(url_for('medicine'))
                except ValueError:
                    flash("Please enter a valid product quantity.", "danger")
                    return redirect(url_for('medicine'))

            # Verify at least one item is being ordered
            if not medicine and not product:
                flash("Please select at least one medicine or product to order.", "danger")
                return redirect(url_for('medicine'))

            # Calculate amount (You can modify this calculation based on your pricing logic)
            if medicine:
                total_amount += medicine_quantity  # Add your pricing logic here
            if product:
                total_amount += product_quantity  # Add your pricing logic here
         
            

            # Create order entry with explicit quantities
            new_order = Medicines(
                mid=form_data['mid'],
                name=form_data['name'],
                medicines=medicine.medicine if medicine else "No medicine ordered",
                products=product.product if product else "No product ordered",
                email=form_data['email'],
                amount=total_amount,
                medicine_quantity=medicine_quantity if medicine else 0,
                product_quantity=product_quantity if product else 0,
                user_id=session['user_id'],  # Ensure this is set
                date=datetime.now().strftime("%Y-%m-%d"),
                status="pending"
            )

            # Update inventory
            if medicine and medicine_quantity > 0:
                medicine.quantity -= medicine_quantity
                
            if product and product_quantity > 0:
                product.quantity -= product_quantity

            # Create log entry with quantity information
            log_entry = Logs(
                mid=form_data['mid'],
                action=f"Ordered medicine: {medicine.medicine if medicine else 'None'} (Qty: {medicine_quantity if medicine else 0}), "
                      f"product: {product.product if product else 'None'} (Qty: {product_quantity if product else 0})",
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user_id=session.get('user_id')
            )

            # Save all changes
            db.session.add(new_order)
            # Process medicine and product orders, update inventory, and create log entry
            # (Code for these steps omitted for brevity, please refer to the original implementation)
            db.session.add(log_entry)
            # Save all changes
            db.session.commit()

            flash("Order placed successfully", "success")
            return redirect(url_for('medicine'))

        except Exception as e:
            print(f"Error: {str(e)}")  # For debugging
            flash("An unexpected error occurred. Please try again.", "danger")
            db.session.rollback()
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
    # Ensure user is logged in
    if request.method == 'POST':
        # Retrieve form data
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
        print("Required fields check:", {
            'mid': bool(form_data['mid']),
            'name': bool(form_data['name']),
            'email': bool(form_data['email'])
        })
        try:
            # Check if the medical ID exists in the Posts table
            medical = Posts.query.filter_by(mid=form_data['mid']).first()
            if not medical:
                flash("Invalid Medical ID. Please register your medical store first.", "danger")
                return redirect(url_for('user_medicines'))

            # Basic validation for required fields
            if not all([form_data['mid'], form_data['name'], form_data['email']]):
                flash("Please fill in all required fields (ID, Name, and Email).", "danger")
                return redirect(url_for('user_medicines'))

            # Verify the name matches the registered medical store
            if medical.medical_name.lower() != form_data['name'].lower():
                flash("Medical store name does not match the registered name for this ID.", "danger")
                return redirect(url_for('user_medicines'))
            
            missing_fields = []
            if not form_data['mid']:
                missing_fields.append("Medical ID")
            if not form_data['name']:
                missing_fields.append("Name")
            if not form_data['email']:
                missing_fields.append("Email")

            if missing_fields:
                flash(f"Please fill in the following required fields: {', '.join(missing_fields)}", "danger")
                return redirect(url_for('medicine'))
            # Process medicine and product orders, update inventory, and create log entry
            # (Code for these steps omitted for brevity, please refer to the original implementation)
            medicine = None
            product = None
            medicine_quantity = 0
            product_quantity = 0
            total_amount = 0

            # Process medicine order if selected
            if form_data['selected_medicine'] and form_data['medicine_quantity']:
                try:
                    medicine_quantity = int(form_data['medicine_quantity'])
                    if medicine_quantity <= 0:
                        flash("Medicine quantity must be greater than 0.", "danger")
                        return redirect(url_for('user_medicines'))
                    
                    medicine = Addmp.query.filter_by(sno=form_data['selected_medicine']).first()
                    if not medicine:
                        flash("Selected medicine not found.", "danger")
                        return redirect(url_for('user_medicines'))
                    
                    if medicine.quantity < medicine_quantity:
                        flash(f"Insufficient medicine stock. Available: {medicine.quantity}", "danger")
                        return redirect(url_for('user_medicines'))
                except ValueError:
                    flash("Please enter a valid medicine quantity.", "danger")
                    return redirect(url_for('user_medicines'))

            # Process product order if selected
            if form_data['selected_product'] and form_data['product_quantity']:
                try:
                    product_quantity = int(form_data['product_quantity'])
                    if product_quantity <= 0:
                        flash("Product quantity must be greater than 0.", "danger")
                        return redirect(url_for('user_medicines'))
                    
                    product = Addpd.query.filter_by(sno=form_data['selected_product']).first()
                    if not product:
                        flash("Selected product not found.", "danger")
                        return redirect(url_for('user_medicines'))
                    
                    if product.quantity < product_quantity:
                        flash(f"Insufficient product stock. Available: {product.quantity}", "danger")
                        return redirect(url_for('user_medicines'))
                except ValueError:
                    flash("Please enter a valid product quantity.", "danger")
                    return redirect(url_for('user_medicines'))

            # Verify at least one item is being ordered
            if not medicine and not product:
                flash("Please select at least one medicine or product to order.", "danger")
                return redirect(url_for('user_medicines'))

            # Calculate amount
            if medicine:
                total_amount += medicine_quantity  # Add your pricing logic here
            if product:
                total_amount += product_quantity  # Add your pricing logic here
    
            
            # Create order entry with explicit quantities
            new_request = Medicines(
                mid=form_data['mid'],
                name=form_data['name'],
                medicines=medicine.medicine if medicine else "No medicine ordered",
                products=product.product if product else "No product ordered",
                email=form_data['email'],
                amount=total_amount,
                medicine_quantity=medicine_quantity if medicine else 0,
                product_quantity=product_quantity if product else 0,
                user_id=session['user_id'],
                date=datetime.now().strftime("%Y-%m-%d"),
                status="pending"
            )

            # Update inventory
            if medicine and medicine_quantity > 0:
                medicine.quantity -= medicine_quantity
            if product and product_quantity > 0:
                product.quantity -= product_quantity

            # Create log entry with quantity information
            log_entry = Logs(
                mid=form_data['mid'],
                action=f"User requested medicine: {medicine.medicine if medicine else 'None'} (Qty: {medicine_quantity if medicine else 0}), "
                      f"product: {product.product if product else 'None'} (Qty: {product_quantity if product else 0})",
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_id=session.get('user_id')
            )
                
            # Save all changes
            db.session.add(new_request)
            db.session.add(log_entry)
            # Save all changes
            db.session.commit()

            flash("Your request has been submitted successfully!", "success")
            return redirect(url_for('user_medicines'))
        except Exception as e:
            print(f"Error: {str(e)}")  # For debugging
            flash("An unexpected error occurred. Please try again.", "danger")
            db.session.rollback()
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