"""
Database seeding utilities
"""
from __init__ import db
from models import User, Wallet
from utils.helpers import generate_unique_id


def create_default_admin():
    """Create default admin user if not exists"""
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if not admin:
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin',
            status='active',
            phone='+1234567890',
            country='United States'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        
        # Create admin wallet
        admin_wallet = Wallet(
            user_id=admin.id,
            wallet_id=generate_unique_id('QP'),
            balance=10000.0
        )
        db.session.add(admin_wallet)
        
        try:
            db.session.commit()
            print("✓ Default admin user created: admin@example.com / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Failed to create admin user: {str(e)}")