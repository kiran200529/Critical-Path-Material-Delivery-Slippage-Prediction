from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import DATABASE_URL, DATABASE_DIR
import os

# Create directory for SQLite if it does not exist
if DATABASE_URL.startswith("sqlite"):
    os.makedirs(DATABASE_DIR, exist_ok=True)

# Create SQLAlchemy engine
# SQLite requires connect_args={'check_same_thread': False}
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    FastAPI Dependency that provides a database session.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Creates tables if they do not exist and populates them with seed data
    if the database is currently empty.
    """
    from backend.models.user import User
    from backend.models.supplier import Supplier
    from backend.models.material import Material
    from backend.models.order import Order
    from backend.models.alert import Alert
    from backend.models.prediction import Prediction
    
    # Create all tables using SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if users table is empty to trigger seeding
        if db.query(User).count() == 0:
            print("Database is empty. Seeding data...")
            
            # Read seed_data.sql or seed manually using Python
            # Seeding manually using Python is much more reliable across SQLite and PostgreSQL
            
            # 1. Add Users
            users = [
                User(name='Sarah Jenkins (Admin)', email='admin@platform.com', password='$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', role='Admin'),
                User(name='David Miller (Procurement)', email='procurement@platform.com', password='$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', role='Procurement Manager'),
                User(name='Elena Rostova (Project)', email='project@platform.com', password='$2b$12$vFvVR8nlwU5.SbzUcmGe5eKH87uwi2GvUY.5oTXX69CcZycqc.Bpu', role='Project Manager')
            ]
            db.add_all(users)
            db.commit()
            
            # 2. Add Suppliers
            suppliers = [
                Supplier(id=1, name='Apex Steel Solutions', supplier_type='Preferred  Framework', risk_score=18, performance_rating=4.8),
                Supplier(id=2, name='London Merchant Goods', supplier_type='Approved  Regional', risk_score=35, performance_rating=4.2),
                Supplier(id=3, name='Midlands MEP Cable Co.', supplier_type='Preferred  Framework', risk_score=12, performance_rating=4.9),
                Supplier(id=4, name='Ready-Mix Concrete Ltd', supplier_type='Approved  Regional', risk_score=28, performance_rating=4.4),
                Supplier(id=5, name='Wales Drywall Merchants', supplier_type='Approved  Regional', risk_score=42, performance_rating=3.9),
                Supplier(id=6, name='Highland Timber Partners', supplier_type='Preferred  Framework', risk_score=22, performance_rating=4.6),
                Supplier(id=7, name='Global MEP Plant Systems', supplier_type='Preferred  Framework', risk_score=15, performance_rating=4.7),
                Supplier(id=8, name='Precast Concrete Specialists', supplier_type='Spot / Non-Framework', risk_score=75, performance_rating=3.1),
                Supplier(id=9, name='Metro Facades & Glazing', supplier_type='Spot / Non-Framework', risk_score=82, performance_rating=2.8),
                Supplier(id=10, name='Rapid Scaffolding Supply', supplier_type='Spot / Non-Framework', risk_score=65, performance_rating=3.4)
            ]
            db.add_all(suppliers)
            db.commit()
            
            # 3. Add Materials
            materials = [
                Material(id=1, material_name='Structural Steel Beams', category='Structural Steel & Metalwork', unit_cost=450.00),
                Material(id=2, material_name='General Drywall Panels', category='Drywall & Finishes', unit_cost=12.50),
                Material(id=3, material_name='Heavy Duty Copper Cable', category='MEP  Cable & Containment', unit_cost=85.00),
                Material(id=4, material_name='High Strength Ready-Mix C40', category='Ready-Mix & Aggregates', unit_cost=120.00),
                Material(id=5, material_name='Premium Softwood Timber Joists', category='Timber & Engineered Wood', unit_cost=45.00),
                Material(id=6, material_name='Industrial HVAC Unit (15kW)', category='MEP  Plant & Equipment', unit_cost=4500.00),
                Material(id=7, material_name='Precast Concrete Stairs', category='Precast & Specialist Concrete', unit_cost=1500.00),
                Material(id=8, material_name='Double-Glazed Facade Panels', category='Facades & Glazing', unit_cost=650.00),
                Material(id=9, material_name='Scaffold Poles & Couplers', category='Scaffolding & Temporary Works', unit_cost=8.50),
                Material(id=10, material_name='Merchant Cement & Aggregates', category='General Merchanted Goods', unit_cost=15.00)
            ]
            db.add_all(materials)
            db.commit()
            
            # 4. Add Orders
            import datetime
            orders = [
                Order(id=1, supplier_id=9, material_id=8, quantity=120, order_date=datetime.date(2026, 5, 10), delivery_date=datetime.date(2026, 6, 15), risk_score=82, risk_level='HIGH', prediction_probability=0.82, region_site='London & South East', project_sector='Commercial / Offices', shipment_mode='Consolidated Hub'),
                Order(id=2, supplier_id=1, material_id=1, quantity=50, order_date=datetime.date(2026, 5, 12), delivery_date=datetime.date(2026, 6, 20), risk_score=18, risk_level='LOW', prediction_probability=0.18, region_site='North West', project_sector='Commercial / Offices', shipment_mode='Full Load  Direct'),
                Order(id=3, supplier_id=8, material_id=7, quantity=30, order_date=datetime.date(2026, 5, 15), delivery_date=datetime.date(2026, 6, 18), risk_score=58, risk_level='MEDIUM', prediction_probability=0.58, region_site='Midlands', project_sector='Healthcare / Education', shipment_mode='Part Load / Groupage'),
                Order(id=4, supplier_id=10, material_id=9, quantity=500, order_date=datetime.date(2026, 5, 20), delivery_date=datetime.date(2026, 6, 10), risk_score=74, risk_level='HIGH', prediction_probability=0.74, region_site='Wales & West', project_sector='Industrial / Logistics', shipment_mode='Consolidated Hub'),
                Order(id=5, supplier_id=3, material_id=3, quantity=200, order_date=datetime.date(2026, 5, 22), delivery_date=datetime.date(2026, 6, 25), risk_score=12, risk_level='LOW', prediction_probability=0.12, region_site='Scotland', project_sector='Infrastructure / Civils', shipment_mode='Full Load  Direct'),
                Order(id=6, supplier_id=6, material_id=5, quantity=150, order_date=datetime.date(2026, 5, 25), delivery_date=datetime.date(2026, 6, 30), risk_score=25, risk_level='LOW', prediction_probability=0.25, region_site='South West', project_sector='Residential', shipment_mode='Courier / Parcel'),
                Order(id=7, supplier_id=2, material_id=10, quantity=1000, order_date=datetime.date(2026, 5, 28), delivery_date=datetime.date(2026, 6, 12), risk_score=45, risk_level='MEDIUM', prediction_probability=0.45, region_site='North East & Yorkshire', project_sector='Commercial / Offices', shipment_mode='Part Load / Groupage')
            ]
            db.add_all(orders)
            db.commit()
            
            # 5. Add Predictions
            predictions = [
                Prediction(order_id=1, probability=0.82, expected_delay_days=6, prediction_timestamp=datetime.datetime(2026, 5, 11, 9, 0, 0)),
                Prediction(order_id=2, probability=0.18, expected_delay_days=0, prediction_timestamp=datetime.datetime(2026, 5, 13, 10, 15, 0)),
                Prediction(order_id=3, probability=0.58, expected_delay_days=3, prediction_timestamp=datetime.datetime(2026, 5, 16, 11, 30, 0)),
                Prediction(order_id=4, probability=0.74, expected_delay_days=5, prediction_timestamp=datetime.datetime(2026, 5, 21, 14, 20, 0)),
                Prediction(order_id=5, probability=0.12, expected_delay_days=0, prediction_timestamp=datetime.datetime(2026, 5, 23, 16, 45, 0)),
                Prediction(order_id=6, probability=0.25, expected_delay_days=1, prediction_timestamp=datetime.datetime(2026, 5, 26, 8, 30, 0)),
                Prediction(order_id=7, probability=0.45, expected_delay_days=2, prediction_timestamp=datetime.datetime(2026, 5, 29, 13, 10, 0))
            ]
            db.add_all(predictions)
            db.commit()
            
            # 6. Add Alerts
            alerts = [
                Alert(order_id=1, alert_type='CRITICAL', message='Delivery of Double-Glazed Facade Panels from Metro Facades & Glazing has a 82% probability of delay. Expected delay: 6 days. This item is on the project critical path.', created_at=datetime.datetime(2026, 5, 11, 9, 5, 0)),
                Alert(order_id=4, alert_type='CRITICAL', message='Delivery of Scaffold Poles & Couplers from Rapid Scaffolding Supply has a 74% probability of delay. Expected delay: 5 days.', created_at=datetime.datetime(2026, 5, 21, 14, 25, 0)),
                Alert(order_id=3, alert_type='WARNING', message='Delivery of Precast Concrete Stairs from Precast Concrete Specialists has a 58% probability of delay. Expected delay: 3 days.', created_at=datetime.datetime(2026, 5, 16, 11, 35, 0))
            ]
            db.add_all(alerts)
            db.commit()
            
            print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
