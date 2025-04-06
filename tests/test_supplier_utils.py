"""
Unit tests for the supplier_utils module.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Import the functions to test
from utils.supplier_utils import get_supplier_by_name_or_create, update_supplier, delete_supplier


class TestSupplierUtils(unittest.TestCase):
    """Test case for the supplier utility functions."""
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_get_supplier_by_name_or_create_new(self, mock_session, mock_supplier_model):
        """Test creating a new supplier."""
        # Setup
        mock_supplier_model.query.filter.return_value.first.return_value = None
        mock_new_supplier = MagicMock()
        mock_supplier_model.return_value = mock_new_supplier
        mock_new_supplier.name = "Test Supplier"
        mock_new_supplier.created_at = datetime.utcnow()
        
        # Call function
        supplier, created = get_supplier_by_name_or_create(
            name="Test Supplier",
            contact_person="Test Person",
            email="test@example.com"
        )
        
        # Assert
        self.assertTrue(created)
        self.assertEqual(supplier, mock_new_supplier)
        mock_session.add.assert_called_once_with(mock_new_supplier)
        mock_session.commit.assert_called_once()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_get_supplier_by_name_or_create_existing(self, mock_session, mock_supplier_model):
        """Test retrieving an existing supplier."""
        # Setup
        mock_existing_supplier = MagicMock()
        mock_existing_supplier.name = "Test Supplier"
        mock_supplier_model.query.filter.return_value.first.return_value = mock_existing_supplier
        
        # Call function
        supplier, created = get_supplier_by_name_or_create(name="Test Supplier")
        
        # Assert
        self.assertFalse(created)
        self.assertEqual(supplier, mock_existing_supplier)
        mock_session.add.assert_not_called()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_get_supplier_by_name_or_create_empty_name(self, mock_session, mock_supplier_model):
        """Test with empty supplier name."""
        # Call function
        supplier, created = get_supplier_by_name_or_create(name="")
        
        # Assert
        self.assertIsNone(supplier)
        self.assertFalse(created)
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_get_supplier_by_name_or_create_integrity_error(self, mock_session, mock_supplier_model):
        """Test handling of IntegrityError."""
        # Setup
        mock_supplier_model.query.filter.return_value.first.return_value = None
        mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
        
        # Setup second query after rollback
        mock_existing_supplier = MagicMock()
        mock_supplier_model.query.filter.return_value.first.side_effect = [None, mock_existing_supplier]
        
        # Call function
        supplier, created = get_supplier_by_name_or_create(name="Test Supplier")
        
        # Assert
        self.assertFalse(created)
        self.assertEqual(supplier, mock_existing_supplier)
        mock_session.rollback.assert_called_once()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_update_supplier_success(self, mock_session, mock_supplier_model):
        """Test successful supplier update."""
        # Setup
        mock_supplier = MagicMock()
        mock_supplier.id = 1
        mock_supplier.name = "Old Name"
        mock_supplier_model.query.get.return_value = mock_supplier
        
        # No other supplier with the same name
        mock_supplier_model.query.filter.return_value.first.return_value = None
        
        # Call function
        result, success, message = update_supplier(
            supplier_id=1,
            name="New Name",
            contact_person="New Contact",
            email="new@example.com",
            is_inhouse=True
        )
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(result, mock_supplier)
        self.assertEqual(result.name, "New Name")
        self.assertEqual(result.contact_person, "New Contact")
        self.assertEqual(result.email, "new@example.com")
        self.assertTrue(result.is_inhouse)
        mock_session.commit.assert_called_once()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_update_supplier_not_found(self, mock_session, mock_supplier_model):
        """Test updating non-existent supplier."""
        # Setup
        mock_supplier_model.query.get.return_value = None
        
        # Call function
        result, success, message = update_supplier(supplier_id=999)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(result)
        self.assertEqual(message, "Supplier not found")
        mock_session.commit.assert_not_called()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_update_supplier_name_exists(self, mock_session, mock_supplier_model):
        """Test updating supplier with a name that already exists for another supplier."""
        # Setup
        mock_supplier = MagicMock()
        mock_supplier.id = 1
        mock_supplier.name = "Old Name"
        mock_supplier_model.query.get.return_value = mock_supplier
        
        # Another supplier with the same name exists
        mock_other_supplier = MagicMock()
        mock_other_supplier.id = 2
        mock_other_supplier.name = "Existing Name"
        mock_supplier_model.query.filter.return_value.first.return_value = mock_other_supplier
        
        # Call function
        result, success, message = update_supplier(
            supplier_id=1,
            name="Existing Name"
        )
        
        # Assert
        self.assertFalse(success)
        self.assertEqual(result, mock_supplier)
        self.assertEqual(message, "A supplier with the name 'Existing Name' already exists")
        mock_session.commit.assert_not_called()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_delete_supplier_success(self, mock_session, mock_supplier_model):
        """Test successful supplier deletion."""
        # Setup
        mock_supplier = MagicMock()
        mock_supplier.id = 1
        mock_supplier.name = "Test Supplier"
        mock_supplier.products = [MagicMock(), MagicMock()]  # 2 related products
        mock_supplier_model.query.get.return_value = mock_supplier
        
        # Call function
        success, message = delete_supplier(supplier_id=1)
        
        # Assert
        self.assertTrue(success)
        self.assertIn("deleted successfully", message)
        self.assertIn("2 related product(s)", message)
        mock_session.delete.assert_called_once_with(mock_supplier)
        mock_session.commit.assert_called_once()
    
    @patch('utils.supplier_utils.Supplier')
    @patch('utils.supplier_utils.db.session')
    def test_delete_supplier_not_found(self, mock_session, mock_supplier_model):
        """Test deleting non-existent supplier."""
        # Setup
        mock_supplier_model.query.get.return_value = None
        
        # Call function
        success, message = delete_supplier(supplier_id=999)
        
        # Assert
        self.assertFalse(success)
        self.assertEqual(message, "Supplier not found")
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()