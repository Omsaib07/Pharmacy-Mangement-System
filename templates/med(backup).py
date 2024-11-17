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