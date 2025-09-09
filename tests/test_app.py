"""
Tests for the Rotax Pro Jet application.
"""

import unittest
import json
from app import app, db, User, Setting

class RotaxProJetTestCase(unittest.TestCase):
    """Test case for the Rotax Pro Jet application."""
    
    def setUp(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_index_page(self):
        """Test that the index page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rotax Pro Jet', response.data)
    
    def test_calculator_page(self):
        """Test that the calculator page loads."""
        response = self.client.get('/calculator')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jetting Calculator', response.data)
    
    def test_jetting_calculation(self):
        """Test the jetting calculation API."""
        data = {
            'temperature': 25,
            'pressure': 1013,
            'humidity': 50,
            'altitude': 100,
            'engine_type': 'Senior MAX EVO'
        }
        
        response = self.client.post(
            '/api/calculate',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        
        # Check that the response contains the expected fields
        self.assertIn('recommendations', result)
        self.assertIn('main_jet', result['recommendations'])
        self.assertIn('needle_position', result['recommendations'])
        self.assertIn('float_height', result['recommendations'])
        self.assertIn('needle_type', result['recommendations'])
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        result = json.loads(response.data)
        self.assertEqual(result['message'], 'User registered successfully')
        
        # Check that the user was created in the database
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test User')
    
    def test_user_login(self):
        """Test user login."""
        # Create a user
        with app.app_context():
            from werkzeug.security import generate_password_hash
            user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.commit()
        
        # Try to log in
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('token', result)

if __name__ == '__main__':
    unittest.main()