import unittest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.validation import validate_email
from app import app, db
from models import Customer, CustomerCategory, CustomerContact
from datetime import datetime, timedelta

class TestEmailValidation(unittest.TestCase):
    """Test the email validation functionality."""
    
    def test_valid_emails(self):
        """Test that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com"
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email))
    
    def test_invalid_emails(self):
        """Test that invalid email addresses fail validation."""
        invalid_emails = [
            "user@",
            "user@.com",
            "@example.com",
            "user@example",
            "user@exam_ple.com",
            "user@exam ple.com",
            "userexample.com"
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email))

class TestDatabaseModels(unittest.TestCase):
    """Test database model relationships and functionality."""
    
    def setUp(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Create test category
        self.test_category = CustomerCategory.query.filter_by(name='Test Category').first()
        if not self.test_category:
            self.test_category = CustomerCategory(name='Test Category', description='For testing')
            db.session.add(self.test_category)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        # Clear test data
        try:
            test_customer = Customer.query.filter_by(name='Test Customer').first()
            if test_customer:
                # Delete related contact history
                contacts = CustomerContact.query.filter_by(customer_id=test_customer.id).all()
                for contact in contacts:
                    db.session.delete(contact)
                
                # Delete customer
                db.session.delete(test_customer)
                db.session.commit()
                
            # Remove test category if it exists
            test_category = CustomerCategory.query.filter_by(name='Test Category').first()
            if test_category:
                db.session.delete(test_category)
                db.session.commit()
        except Exception as e:
            print(f"Error in tearDown: {e}")
            db.session.rollback()
        
        self.app_context.pop()
    
    def test_customer_category_assignment(self):
        """Test that customers can be assigned to categories."""
        try:
            # Create a test customer with a category
            test_customer = Customer(
                name='Test Customer',
                email='test@example.com',
                phone='123-456-7890',
                address='123 Test St',
                category_id=self.test_category.id
            )
            db.session.add(test_customer)
            db.session.commit()
            
            # Verify the customer is assigned to the category
            self.assertEqual(test_customer.category_id, self.test_category.id)
            
            # Verify the relationship works (customer belongs to the category)
            self.assertEqual(test_customer.category.name, 'Test Category')
        except Exception as e:
            db.session.rollback()
            self.fail(f"Customer category assignment test failed: {e}")
    
    def test_contact_history_creation(self):
        """Test that contact history entries can be created for customers."""
        try:
            # Create a test customer
            test_customer = Customer(
                name='Test Customer',
                email='test@example.com',
                phone='123-456-7890',
                address='123 Test St',
                category_id=self.test_category.id
            )
            db.session.add(test_customer)
            db.session.commit()
            
            # Create contact history entry
            contact_date = datetime.utcnow() - timedelta(days=1)
            contact = CustomerContact(
                customer_id=test_customer.id,
                contact_date=contact_date,
                contact_type='email',
                notes='Test contact history entry'
            )
            db.session.add(contact)
            db.session.commit()
            
            # Verify the contact was created and linked to the customer
            self.assertEqual(contact.customer_id, test_customer.id)
            
            # Verify the relationship works (contact belongs to the customer)
            self.assertEqual(contact.customer.name, 'Test Customer')
            
            # Check the contact appears in the customer's contacts
            self.assertEqual(len(test_customer.contacts), 1)
            self.assertEqual(test_customer.contacts[0].notes, 'Test contact history entry')
        except Exception as e:
            db.session.rollback()
            self.fail(f"Contact history creation test failed: {e}")


if __name__ == '__main__':
    unittest.main()