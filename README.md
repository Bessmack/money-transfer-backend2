# Money Transfer Backend API

A Flask-based REST API for a money transfer application with user authentication, wallet management, and transaction processing.

## Features

- 🔐 **User Authentication** - JWT-based authentication with registration and login
- 💰 **Wallet Management** - Digital wallet system for each user
- 💸 **Money Transfers** - Send money between users with transaction fees
- 👥 **Beneficiary Management** - Save and manage frequent recipients
- 📊 **Admin Dashboard** - Administrative functions for user and transaction management
- 🔒 **Security** - Password hashing, JWT tokens, and role-based access control

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-Bcrypt** - Password hashing
- **Flask-CORS** - Cross-Origin Resource Sharing
- **SQLite/PostgreSQL** - Database

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

6. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | User login | No |
| GET | `/api/auth/me` | Get current user | Yes |

### User Profile

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/profile` | Get user profile | Yes |
| PUT | `/api/users/profile` | Update user profile | Yes |
| POST | `/api/users/change-password` | Change password | Yes |

### Wallet

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/wallet` | Get user wallet | Yes |
| POST | `/api/wallet/add-funds` | Add funds to wallet | Yes |

### Transactions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/transactions/send` | Send money to user | Yes |
| GET | `/api/transactions` | Get user transactions | Yes |
| GET | `/api/transactions/<id>` | Get transaction details | Yes |

### Beneficiaries

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/beneficiaries` | Get all beneficiaries | Yes |
| POST | `/api/beneficiaries` | Add new beneficiary | Yes |
| GET | `/api/beneficiaries/<id>` | Get beneficiary details | Yes |
| PUT | `/api/beneficiaries/<id>` | Update beneficiary | Yes |
| DELETE | `/api/beneficiaries/<id>` | Delete beneficiary | Yes |

### Admin Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/users` | Get all users | Admin |
| GET | `/api/admin/users/<id>` | Get user details | Admin |
| PUT | `/api/admin/users/<id>` | Update user | Admin |
| DELETE | `/api/admin/users/<id>` | Delete user | Admin |
| GET | `/api/admin/wallets` | Get all wallets | Admin |
| POST | `/api/admin/wallets/<id>/adjust` | Adjust wallet balance | Admin |
| GET | `/api/admin/transactions` | Get all transactions | Admin |
| GET | `/api/admin/stats` | Get system statistics | Admin |

## Request/Response Examples

### Register User

**Request:**
```json
POST /api/auth/register
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "user",
    "status": "active"
  },
  "wallet": {
    "id": 1,
    "wallet_id": "QP-ABC123XYZ",
    "balance": 0.0,
    "currency": "USD"
  }
}
```

### Login

**Request:**
```json
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }
}
```

### Send Money

**Request:**
```json
POST /api/transactions/send
Authorization: Bearer <access_token>
{
  "receiver_id": 2,
  "amount": 100.00,
  "note": "Payment for services"
}
```

**Response:**
```json
{
  "message": "Money sent successfully",
  "transaction": {
    "transaction_id": "TXN1234567",
    "sender_id": 1,
    "receiver_id": 2,
    "amount": 100.00,
    "fee": 0.50,
    "total_amount": 100.50,
    "status": "completed"
  },
  "wallet": {
    "balance": 899.50
  }
}
```

### Add Funds

**Request:**
```json
POST /api/wallet/add-funds
Authorization: Bearer <access_token>
{
  "amount": 500.00,
  "note": "Adding funds via credit card"
}
```

**Response:**
```json
{
  "message": "Funds added successfully",
  "wallet": {
    "balance": 1399.50
  },
  "transaction": {
    "transaction_id": "TXN1234568",
    "type": "add_funds",
    "amount": 500.00
  }
}
```

## Database Schema

### Users Table
- id (Primary Key)
- first_name
- last_name
- email (Unique)
- password_hash
- phone
- country
- address
- city
- zip_code
- role (user/admin)
- status (active/inactive)
- created_at
- updated_at

### Wallets Table
- id (Primary Key)
- user_id (Foreign Key)
- wallet_id (Unique)
- balance
- currency
- status
- created_at
- updated_at

### Transactions Table
- id (Primary Key)
- transaction_id (Unique)
- sender_id (Foreign Key)
- receiver_id (Foreign Key)
- amount
- fee
- total_amount
- type
- status
- note
- created_at

### Beneficiaries Table
- id (Primary Key)
- user_id (Foreign Key)
- name
- email
- phone
- relationship
- created_at

## Configuration

### Environment Variables

- `FLASK_ENV` - Environment (development/production)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key
- `DATABASE_URL` - Database connection string
- `PORT` - Server port (default: 5000)

### Transaction Settings

- Transaction fee: 0.5% of amount
- Minimum transaction: $1.00
- Maximum transaction: $10,000.00

## Default Admin Account

**Email:** admin@example.com  
**Password:** admin123

⚠️ **Change these credentials immediately in production!**

## Security Features

- Password hashing with Bcrypt
- JWT token-based authentication
- Role-based access control (User/Admin)
- CORS protection
- SQL injection prevention via ORM
- Input validation

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses follow this format:
```json
{
  "error": "Error message description"
}
```

## Testing

You can test the API using:
- Postman
- cURL
- Python requests library
- Frontend application

Example cURL request:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

## Deployment

### Production Checklist

1. ✅ Change default admin credentials
2. ✅ Set strong SECRET_KEY and JWT_SECRET_KEY
3. ✅ Use PostgreSQL instead of SQLite
4. ✅ Enable HTTPS
5. ✅ Set DEBUG=False
6. ✅ Configure proper CORS origins
7. ✅ Set up proper logging
8. ✅ Use environment variables for sensitive data

### Using Gunicorn (Production Server)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

For issues, questions, or contributions, please contact the development team.

## License

MIT License