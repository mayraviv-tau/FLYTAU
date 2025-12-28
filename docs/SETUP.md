# FLYTAU Setup Guide

Complete setup guide for the FLYTAU flight booking system.

## Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Project
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE flytau;

# Use the database
USE flytau;

# Import schema
SOURCE db/schema.sql;

# Import seed data
SOURCE db/seed.sql;

# Exit MySQL
EXIT;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and set your database credentials:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=flytau
DB_USER=root
DB_PASSWORD=your_mysql_password_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

**Generate a secret key:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the Server

```bash
# From project root
cd app/server
python main.py
```

Or using Flask CLI:

```bash
export FLASK_APP=app.server.main:app
flask run
```

The server will start at `http://localhost:5000`

### 7. Verify Installation

Test the health endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "FLYTAU API"
}
```

## Running Tests

```bash
# From project root
pytest
```

Run tests with coverage:

```bash
pytest --cov=app/server --cov-report=html
```

## Development Workflow

### Starting the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
cd app/server
python main.py
```

### Database Management

**Reset database:**

```bash
mysql -u root -p flytau < db/schema.sql
mysql -u root -p flytau < db/seed.sql
```

**View reports:**

```bash
mysql -u root -p flytau < db/reports_sql/report_1.sql
```

### Testing API Endpoints

Use curl, Postman, or any HTTP client.

**Example: Register a customer**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "first_name": "Test",
    "last_name": "User",
    "birth_date": "1990-01-15",
    "passport_number": "T12345678"
  }'
```

**Example: Login**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "user_type": "customer"
  }'
```

**Example: Search flights (with authentication)**

```bash
curl -X GET "http://localhost:5000/api/flights?origin=TLV" \
  -b cookies.txt
```

## Seed Data

The database includes sample data:

**Customers:**
- alice.thompson@gmail.com (registered, balance: $1500)
- michael.chen@yahoo.com (registered, balance: $200)

**Managers:**
- ID: 200000001, Password: manager123 (משה כהן)
- ID: 200000002, Password: manager456 (שרה לוי)

**Flights:**
- Flight 1: TLV → JFK (2026-04-01)
- Flight 2: TLV → ETM (2026-04-02)
- Flight 3: TLV → LHR (2026-04-05)
- Flight 4: ETM → TLV (2026-04-06)

## Troubleshooting

### Connection to Database Failed

Check:
- MySQL is running: `mysql --version`
- Database exists: `mysql -u root -p -e "SHOW DATABASES;"`
- Credentials in `.env` are correct

### Module Not Found Errors

Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

Change the port in `.env`:
```bash
FLASK_PORT=8000
```

### Session Not Persisting

Check that `flask_session/` directory exists:
```bash
mkdir -p app/server/flask_session
```

## Production Deployment

### Configuration Changes

1. Set environment to production:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

2. Use a strong secret key
3. Enable HTTPS
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Set up reverse proxy (Nginx)

### Example with Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 "app.server.main:app"
```

## Additional Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
