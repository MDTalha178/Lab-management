<<<<<<< HEAD
# Lab-management
=======
# Lab Management System - Multi-Tenant Application

A production-ready Django REST Framework backend for managing laboratory operations with complete multi-tenant isolation.

## 🚀 Features

- **Multi-Tenant Architecture**: Complete data isolation using single-database approach
- **Role-Based Access Control (RBAC)**: Tenant Admin and Tenant User roles
- **Patient Management**: Comprehensive patient records with medical history
- **Test Management**: Test ordering, tracking, and result management
- **Sample Management**: Sample collection, processing, and quality control
- **JWT Authentication**: Secure token-based authentication
- **API Documentation**: Auto-generated Swagger/ReDoc documentation
- **Production-Ready**: Configured with security best practices

## 📋 Requirements

- Python 3.10+
- PostgreSQL 13+
- pip/virtualenv

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd lab_management
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=lab_management
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 5. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE lab_management;
CREATE USER postgres WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE lab_management TO postgres;
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## 🔐 Authentication Flow

### 1. Register a Tenant

```bash
POST /api/tenants/register/
Content-Type: application/json

{
    "name": "Lab A",
    "contact_email": "admin@laba.com",
    "contact_phone": "+1234567890",
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001",
    "admin_email": "admin@laba.com",
    "admin_password": "SecurePass123!",
    "admin_first_name": "John",
    "admin_last_name": "Doe",
    "admin_address_line1": "123 Main St",
    "admin_city": "New York",
    "admin_state": "NY",
    "admin_country": "USA",
    "admin_postal_code": "10001"
}
```

### 2. Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
    "email": "admin@laba.com",
    "password": "SecurePass123!"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "email": "admin@laba.com",
        "role": "tenant_admin",
        "tenant_id": 1,
        "tenant_name": "Lab A"
    }
}
```

### 3. Use Access Token

Include the access token in the Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🧪 Example API Calls

### Create a Patient

```bash
POST /api/patients/patients/
Authorization: Bearer <token>
Content-Type: application/json

{
    "patient_id": "P001",
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "phone_number": "+1234567890",
    "address_line1": "456 Oak Ave",
    "city": "Boston",
    "state": "MA",
    "country": "USA",
    "postal_code": "02101",
    "blood_group": "A+"
}
```

### Create a Test Type

```bash
POST /api/patients/test-types/
Authorization: Bearer <token>
Content-Type: application/json

{
    "code": "CBC",
    "name": "Complete Blood Count",
    "category": "Blood Test",
    "price": "50.00",
    "estimated_duration_hours": 24,
    "requires_sample": true,
    "sample_type": "Blood",
    "sample_volume_ml": "5.0"
}
```

### Order a Test

```bash
POST /api/patients/tests/
Authorization: Bearer <token>
Content-Type: application/json

{
    "patient": 1,
    "test_type": 1,
    "priority": "routine",
    "clinical_notes": "Annual checkup"
}
```

### Collect a Sample

```bash
POST /api/patients/samples/
Authorization: Bearer <token>
Content-Type: application/json

{
    "test": 1,
    "sample_type": "Blood",
    "volume_ml": "5.0",
    "collected_at": "2024-01-15T10:30:00Z",
    "collection_method": "Venipuncture"
}
```

## 👥 User Roles & Permissions

### Tenant Admin (`tenant_admin`)
- Create, read, update, delete users within their tenant
- Manage all domain data (patients, tests, samples, test types)
- Full access to all tenant resources

### Tenant User (`tenant_user`)
- Create and view patient/test/sample-related resources
- Cannot manage users
- Cannot delete critical data

## 🏗️ Project Structure

```
lab_management/
├── config/              # Project configuration
├── apps/
│   ├── core/           # Core functionality (middleware, permissions)
│   ├── tenants/        # Tenant management
│   ├── accounts/       # User authentication
│   └── patients/       # Domain models (Patient, Test, Sample)
└── tests/              # Test files
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

## 🔒 Security Features

- JWT-based authentication with token refresh
- Password hashing with Django's default PBKDF2
- Role-based access control (RBAC)
- Tenant isolation at middleware level
- SQL injection protection (Django ORM)
- CORS configuration
- Rate limiting
- Secure headers in production

## 🧪 Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=apps --cov-report=html
```

## 📦 Database Schema

Key models and relationships:

- **Tenant**: Organization/lab entity
- **User**: Belongs to one tenant, has role
- **Patient**: Tenant-scoped patient records
- **TestType**: Configurable test definitions per tenant
- **Test**: Links patient to test type
- **Sample**: Physical samples for tests

All domain models inherit from `TenantAwareModel` for automatic tenant filtering.

## 🚀 Production Deployment

### Environment Variables

Update `.env` for production:

```env
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Run with Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Database Backups

```bash
pg_dump lab_management > backup.sql
```

## 📝 License

This project is for assignment purposes.

## 👨‍💻 Author

Developed as part of application process demonstrating 4+ years Python/Django expertise.

## 📞 Support

For issues or questions, please refer to the API documentation or contact support.
>>>>>>> 97b38bd10b77b22b605d2a4ad0c8184104b9051a
