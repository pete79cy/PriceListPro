"""
Test the email validation in supplier operations
"""
import unittest
from unittest.mock import patch, MagicMock
from utils.validation import validate_email

class TestEmailValidation(unittest.TestCase):
    """Test email validation in supplier operations"""
    
    def test_validate_email_function(self):
        """Test that the validate_email function works correctly"""
        # Valid emails
        self.assertTrue(validate_email("supplier@example.com"))
        self.assertTrue(validate_email("supplier.name@example.com"))
        self.assertTrue(validate_email("supplier+tag@example.com"))
        
        # Invalid emails
        self.assertFalse(validate_email(""))
        self.assertFalse(validate_email(None))
        self.assertFalse(validate_email("supplier@"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("supplier@example"))
        self.assertFalse(validate_email("supplier@exam_ple.com"))

    @patch('utils.supplier_utils.validate_email')
    def test_supplier_create_with_invalid_email(self, mock_validate_email):
        """Test that creating a supplier with invalid email fails"""
        from utils.supplier_utils import get_supplier_by_name_or_create
        
        # Mock the validate_email function to return False
        mock_validate_email.return_value = False
        
        # Call the function with an email
        supplier, created = get_supplier_by_name_or_create(
            name="Test Supplier",
            email="invalid-email"
        )
        
        # Verify validate_email was called
        mock_validate_email.assert_called_once_with("invalid-email")
        
        # Should return None, False for validation failure
        self.assertIsNone(supplier)
        self.assertFalse(created)

    @patch('utils.supplier_utils.validate_email')
    @patch('utils.supplier_utils.Supplier')
    def test_supplier_update_with_invalid_email(self, mock_supplier_model, mock_validate_email):
        """Test that updating a supplier with invalid email fails"""
        from utils.supplier_utils import update_supplier
        
        # Mock the validate_email function to return False
        mock_validate_email.return_value = False
        
        # Mock a supplier object
        mock_supplier = MagicMock()
        mock_supplier.id = 1
        mock_supplier_model.query.get.return_value = mock_supplier
        
        # Call the function with an invalid email
        result, success, message = update_supplier(
            supplier_id=1,
            email="invalid-email"
        )
        
        # Verify validate_email was called
        mock_validate_email.assert_called_once_with("invalid-email")
        
        # Should return False with the appropriate message
        self.assertEqual(result, mock_supplier)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid email address format")

if __name__ == '__main__':
    unittest.main()