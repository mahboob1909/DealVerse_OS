# DealVerse OS Backend

AI-powered investment banking platform backend built with FastAPI, PostgreSQL, and modern Python technologies.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or Neon account)
- Redis (optional, for caching and background tasks)
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Neon PostgreSQL Database**
   - Sign up at [neon.com](https://neon.com)
   - Create a new project
   - Copy the connection string to your `.env` file

5. **Initialize the database**
   ```bash
   # Activate virtual environment
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Initialize database
   python -c "from app.db.database import init_db; init_db()"
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Setup

1. **Run Docker setup**
   ```bash
   python setup.py --docker
   ```

2. **Start all services**
   ```bash
   docker-compose up
   ```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                 # API routes and endpoints
│   │   ├── api_v1/
│   │   │   ├── endpoints/   # Individual endpoint modules
│   │   │   └── api.py       # API router configuration
│   │   └── deps.py          # API dependencies
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Authentication & security
│   ├── crud/                # Database operations
│   ├── db/                  # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # FastAPI application
├── scripts/                 # Database and setup scripts
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dealverse_db
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dealverse_db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# File Storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=dealverse-documents
```

## 🗄️ Database

### Models

- **Organization**: Multi-tenant organization management
- **User**: User authentication and profiles
- **Deal**: Investment banking deals and transactions
- **Client**: Client relationship management
- **Task**: Project and task management
- **Document**: File storage and document management
- **FinancialModel**: Financial modeling and valuation

### Migrations

Using SQLAlchemy for database schema management:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🔐 Authentication

JWT-based authentication with role-based access control (RBAC):

- **Roles**: admin, manager, analyst, associate, vp
- **Permissions**: Granular permissions for different operations
- **Multi-tenancy**: Organization-based data isolation

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token

### Core Resources
- `/api/v1/users` - User management
- `/api/v1/organizations` - Organization management
- `/api/v1/deals` - Deal management
- `/api/v1/clients` - Client management
- `/api/v1/tasks` - Task management
- `/api/v1/documents` - Document management
- `/api/v1/financial-models` - Financial modeling

### Documentation
- `/api/v1/docs` - Interactive API documentation (Swagger UI)
- `/api/v1/redoc` - Alternative API documentation (ReDoc)

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## 🚀 Deployment

### Production Checklist

1. **Environment Configuration**
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure production database

2. **Security**
   - Enable HTTPS
   - Set proper CORS origins
   - Configure rate limiting
   - Set up monitoring

3. **Database**
   - Use production PostgreSQL (Neon recommended)
   - Set up database backups
   - Configure connection pooling

4. **Monitoring**
   - Set up Sentry for error tracking
   - Configure structured logging
   - Set up health checks

### Docker Production

```bash
# Build production image
docker build -t dealverse-backend .

# Run with production settings
docker run -p 8000:8000 --env-file .env.production dealverse-backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and linting
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
