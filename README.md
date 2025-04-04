# Plant Pricing System

A comprehensive plant pricing management system with a modern React frontend and Flask backend.

## Project Structure

The project is organized into two main directories:

- `backend/`: Flask-based backend with API endpoints
- `frontend/`: React-based frontend with TypeScript

## Setup Instructions

### Backend Setup

1. Make sure Python is installed on your system.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL database connection string
   - `SESSION_SECRET`: Secret key for session management

### Frontend Setup

1. Make sure Node.js is installed on your system.
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install the required npm packages:
   ```
   npm install
   ```
4. Build the frontend for production:
   ```
   npm run build
   ```

## Running the Application

### Development Mode

1. Start the backend:
   ```
   python main.py
   ```
2. In a separate terminal, start the frontend:
   ```
   cd frontend
   npm start
   ```

### Production Mode

1. Build the frontend:
   ```
   cd frontend
   npm run build
   ```
2. Start the backend server, which will serve the frontend:
   ```
   python main.py
   ```

## Features

- **User Authentication**: Secure login and role-based access
- **Customer Management**: Add, edit, and manage customers
- **Product Management**: Manage plant products, with scientific names and other details
- **Price List Management**: Set customer-specific pricing for products
- **Quotation Generation**: Create and export quotations
- **Invoice Management**: Track customer invoices
- **Document Import**: Extract data from Excel spreadsheets and PDF documents
- **API Access**: RESTful API for all operations

## Technologies Used

### Backend
- Python
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-Login for authentication
- Pandas for data processing

### Frontend
- React
- TypeScript
- React Router
- Bootstrap
- Axios for API calls

## License

This project is licensed under the MIT License - see the LICENSE file for details.