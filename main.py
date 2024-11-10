from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask import Flask, render_template, request, session, redirect, flash, url_for
# Load configuration parameters
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Configure SQLAlchemy with MySQL Connector
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Omsai7%40sql@localhost/Medical'
# Initialize the database
db = SQLAlchemy(app)

# Define Models
class Medicines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    medicines = db.Column(db.String(500), nullable=False)
    products = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mid = db.Column(db.String(120), nullable=False)
    medicine_quantity = db.Column(db.Integer, default=0)  # New column
    product_quantity = db.Column(db.Integer, default=0)   # New column

class Posts(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    medical_name = db.Column(db.String(80), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(120), nullable=False)

class Addmp(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Addpd(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Logs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String, nullable=True)
    action = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(100), nullable=False)



@app.route("/")
def hello():

    return render_template('index.html', params=params)

@app.route("/")
def home():
    return redirect(url_for('dashboard.html'))

@app.route("/search",methods=['GET','POST'])
def search():

    if request.method == 'POST':

        name = request.form.get('search')
        post = Addmp.query.filter_by(medicine=name).first()
        pro = Addpd.query.filter_by(product=name).first()

        if (post or pro):
            flash("Item Is Available.", "primary")

        else:
            flash("Item is not Available.", "danger")


    return render_template('search.html', params=params)

@app.route("/details", methods=['GET','POST'])
def details():

    if ('user' in session and session['user'] == params['user']):
        posts =Logs.query.all()
        return render_template('details.html', params=params, posts=posts)





@app.route("/insert", methods = ['GET','POST'])
def insert():


    if (request.method == 'POST'):
        '''ADD ENTRY TO THE DATABASE'''
        mid=request.form.get('mid')

        medical_name = request.form.get('medical_name')
        owner_name = request.form.get('owner_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        push = Posts(mid=mid,medical_name=medical_name, owner_name=owner_name, phone_no=phone_no, address=address)
        db.session.add(push)
        db.session.commit()

        flash("Thanks for submitting your details","danger")


    return render_template('insert.html',params=params)


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

@app.route("/list",methods=['GET','POST'])
def post():

    if ('user' in session and session['user'] == params['user']):

        posts=Medicines.query.all()
        return render_template('post.html', params=params, posts=posts)


@app.route("/items",methods=['GET','POST'])
def items():

    if ('user' in session and session['user'] == params['user']):

        posts=Addmp.query.all()
        return render_template('items.html', params=params,posts=posts)


@app.route("/items2", methods=['GET','POST'])
def items2():

    if ('user' in session and session['user'] == params['user']):


        posts=Addpd.query.all()
        return render_template('items2.html',params=params,posts=posts)


@app.route("/sp",methods=['GET','POST'])
def sp():

    if ('user' in session and session['user'] == params['user']):

        posts=Medicines.query.all()
        return render_template('store.html', params=params,posts=posts)


@app.route("/logout")
def logout():

    session.pop('user')
    flash("You are logout", "primary")

    return redirect('/login')


@app.route("/login",methods=['GET','POST'])
def login():

    if ('user' in session and session['user'] == params['user']):
        posts = Posts.query.all()
        return render_template('dashbord.html',params=params,posts=posts)

    if request.method=='POST':

        username=request.form.get('uname')
        userpass=request.form.get('password')
        if(username==params['user'] and userpass==params['password']):

            session['user']=username
            posts=Posts.query.all()
            flash("You are Logged in", "primary")

            return render_template('index.html',params=params,posts=posts)
        else:
            flash("wrong password", "danger")

    return render_template('login.html', params=params)


@app.route("/edit/<string:mid>",methods=['GET','POST'])

def edit(mid):
    if('user' in session and session['user']==params['user']):
        if request.method =='POST':
            medical_name=request.form.get('medical_name')
            owner_name=request.form.get('owner_name')
            phone_no=request.form.get('phone_no')
            address=request.form.get('address')


            if mid==0:
                posts=Posts(medical_name=medical_name,owner_name=owner_name,phone_no=phone_no,address=address)

                db.session.add(posts)
                db.session.commit()
            else:
                post=Posts.query.filter_by(mid=mid).first()
                post.medical_name=medical_name
                post.owner_name=owner_name
                post.phone_no=phone_no
                post.address=address
                db.session.commit()
                flash("Data Updated Succesfully ", "success")

                return redirect('/edit/'+mid)
        post = Posts.query.filter_by(mid=mid).first()
        return render_template('edit.html',params=params,post=post)


#         if user is logged in
#delete

@app.route("/delete/<string:mid>", methods=['GET', 'POST'])
def delete(mid):
    if ('user' in session and session['user']==params['user']):
        post=Posts.query.filter_by(mid=mid).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "warning")

    return redirect('/login')

# Add this route to your Flask application
@app.route("/deletemp/<int:id>", methods=['GET', 'POST'])
def delete_order(id):
    try:
        if ('user' in session and session['user'] == params['user']):
            # Find the order to be deleted
            order = Medicines.query.filter_by(id=id).first()
            
            if order:
                # Restore quantities to inventory before deleting the order
                if order.medicine_quantity > 0 and order.medicines != "No medicine ordered":
                    medicine = Addmp.query.filter_by(medicine=order.medicines).first()
                    if medicine:
                        medicine.quantity += order.medicine_quantity
                
                if order.product_quantity > 0 and order.products != "No product ordered":
                    product = Addpd.query.filter_by(product=order.products).first()
                    if product:
                        product.quantity += order.product_quantity
                
                # Create log entry for the deletion
                log_entry = Logs(
                    mid=order.mid,
                    action=f"Deleted order - Medicine: {order.medicines} (Qty: {order.medicine_quantity}), "
                          f"Product: {order.products} (Qty: {order.product_quantity})",
                    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Add log entry and delete order
                db.session.add(log_entry)
                db.session.delete(order)
                db.session.commit()
                
                flash("Order deleted successfully and inventory restored", "success")
            else:
                flash("Order not found", "danger")
                
        else:
            flash("Please login to delete orders", "danger")
            return redirect(url_for('login'))
            
    except Exception as e:
        print(f"Error deleting order: {str(e)}")  # For debugging
        db.session.rollback()
        flash("Error occurred while deleting the order", "danger")
    
    return redirect(url_for('sp'))  # Redirect to the orders page
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, flash, url_for
@app.route("/verify_mid/<mid>")
def verify_mid(mid):
    medical = Posts.query.filter_by(mid=mid).first()
    if medical:
        return jsonify({
            'exists': True,
            'name': medical.medical_name
        })
    return jsonify({'exists': False})
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

            # Initialize variables
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
                product_quantity=product_quantity if product else 0
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
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # Save all changes
            db.session.add(new_order)
            db.session.add(log_entry)
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
app.run(debug=True)