"""
Database initialization script for Rotax Pro Jet.

This script creates the initial database structure and adds some sample data.
Run this script after setting up your environment but before starting the application.
"""

import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from app import User, Setting

def init_db():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have users
        if User.query.count() > 0:
            print("Database already initialized. Skipping sample data creation.")
            return
        
        # Create sample users
        print("Creating sample users...")
        users = [
            {
                'name': 'John Smith',
                'email': 'john@example.com',
                'password': generate_password_hash('password123'),
                'subscription_plan': 'pro',
                'subscription_end_date': datetime.utcnow() + timedelta(days=30)
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah@example.com',
                'password': generate_password_hash('password123'),
                'subscription_plan': 'basic',
                'subscription_end_date': datetime.utcnow() + timedelta(days=30)
            },
            {
                'name': 'Michael Chen',
                'email': 'michael@example.com',
                'password': generate_password_hash('password123'),
                'subscription_plan': 'team',
                'subscription_end_date': datetime.utcnow() + timedelta(days=30)
            }
        ]
        
        for user_data in users:
            user = User(**user_data)
            db.session.add(user)
        
        # Commit users to get their IDs
        db.session.commit()
        
        # Create sample settings for the first user
        print("Creating sample settings...")
        john = User.query.filter_by(email='john@example.com').first()
        
        settings = [
            {
                'user_id': john.id,
                'name': 'Summer Setup - ABC Track',
                'notes': 'Hot day, track was in good condition',
                'temperature': 30.5,
                'pressure': 1013.2,
                'humidity': 65,
                'altitude': 100,
                'engine_type': 'Senior MAX EVO',
                'reference_jet': 130,
                'main_jet': 128,
                'needle_position': 3,
                'float_height': 15.2,
                'needle_type': 'K98',
                'created_at': datetime.utcnow() - timedelta(days=5)
            },
            {
                'user_id': john.id,
                'name': 'Winter Setup - XYZ Track',
                'notes': 'Cold day, track was slippery',
                'temperature': 10.2,
                'pressure': 1020.5,
                'humidity': 40,
                'altitude': 150,
                'engine_type': 'Senior MAX EVO',
                'reference_jet': 130,
                'main_jet': 134,
                'needle_position': 2,
                'float_height': 14.8,
                'needle_type': 'K98',
                'created_at': datetime.utcnow() - timedelta(days=60)
            }
        ]
        
        for setting_data in settings:
            setting = Setting(**setting_data)
            db.session.add(setting)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()