from app import app, db, Posts, Addmp, Addpd

with app.app_context():
    # Create test medical store
    store = Posts(mid='MED001', medical_name='Test Pharmacy')
    
    # Create test medicines
    med1 = Addmp(medicine='Paracetamol', quantity=100, medicine_price=5.0)
    med2 = Addmp(medicine='Aspirin', quantity=150, medicine_price=3.0)
    
    # Create test products
    prod1 = Addpd(product='Bandages', quantity=50, product_price=2.0)
    prod2 = Addpd(product='Antiseptic', quantity=75, product_price=4.0)
    
    db.session.add_all([store, med1, med2, prod1, prod2])
    db.session.commit()