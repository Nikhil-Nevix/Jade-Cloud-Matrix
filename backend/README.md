# JADE Cloud Matrix — Backend

FastAPI backend for the JADE Cloud Matrix cloud pricing intelligence platform.

## Architecture

### Core Components

- **FastAPI** — Modern async web framework
- **SQLAlchemy 2.0** — Async ORM with PostgreSQL
- **Alembic** — Database migrations
- **JWT Authentication** — Secure token-based auth
- **APScheduler** — Background job scheduling
- **Anthropic Claude API** — AI-powered recommendations

### Directory Structure

```
app/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management (pydantic-settings)
├── database.py             # SQLAlchemy async engine & session
├── dependencies.py         # FastAPI dependencies (auth, db)
│
├── core/
│   ├── security.py         # JWT, bcrypt, OAuth2
│   └── audit.py            # Audit logging
│
├── models/                 # SQLAlchemy models (9 files)
│   ├── user.py
│   ├── provider.py
│   ├── pricing.py          # compute + storage
│   ├── reserved_pricing.py
│   ├── kubernetes_pricing.py
│   ├── network_pricing.py
│   ├── calculation.py
│   ├── budget.py
│   └── audit_log.py
│
├── schemas/                # Pydantic schemas (11 files)
│   ├── auth.py
│   ├── user.py
│   ├── provider.py
│   ├── pricing.py
│   ├── reserved_pricing.py
│   ├── kubernetes_pricing.py
│   ├── network_pricing.py
│   ├── calculation.py
│   ├── budget.py
│   ├── recommendation.py
│   └── audit_log.py
│
├── routers/                # API endpoints (12 routers)
│   ├── health.py           # Health check
│   ├── auth.py             # Login, register, me
│   ├── providers.py        # Cloud providers & regions
│   ├── pricing.py          # Compute & storage pricing
│   ├── reserved.py         # Reserved instance pricing
│   ├── kubernetes.py       # Kubernetes pricing
│   ├── network.py          # Network transfer pricing
│   ├── calculations.py     # Calculation CRUD & history
│   ├── budgets.py          # Budget management
│   ├── recommendations.py  # AI recommendations (Claude)
│   ├── admin.py            # Admin operations
│   └── export.py           # PDF & Excel export
│
└── services/               # Business logic
    ├── pricing_engine.py       # Standard pricing calculations
    ├── reserved_engine.py      # Reserved instance calculations
    ├── kubernetes_engine.py    # Kubernetes cost modeling
    ├── network_engine.py       # Network transfer calculations
    ├── comparison_engine.py    # Cross-provider comparison
    ├── budget_service.py       # Budget tracking
    ├── ai_recommendations.py   # Claude API integration
    ├── ingestion/
    │   ├── scheduler.py        # APScheduler setup
    │   ├── runner.py           # Orchestrates ingestion
    │   ├── aws_ingester.py     # AWS pricing API
    │   ├── azure_ingester.py   # Azure pricing API
    │   ├── gcp_ingester.py     # GCP pricing API
    │   └── fallback_data.py    # Hardcoded fallback prices
    └── export/
        ├── pdf_exporter.py     # PDF generation (ReportLab)
        └── excel_exporter.py   # Excel generation (openpyxl)
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# Database
DATABASE_URL=postgresql+asyncpg://jade_user:jade_pass@localhost:5432/jade_db

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your-secure-random-string-minimum-32-characters

# Claude API (required for AI recommendations)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# CORS (add your frontend URL)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Database Setup

```bash
# Create database and user
sudo -u postgres psql -f ../db_setup.sql

# Run migrations
alembic upgrade head

# Seed initial data (providers, regions, users, pricing)
python scripts/seed.py
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: **http://localhost:8000**

---

## API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All endpoints except `/api/healthz` and `/api/v1/auth/login` require authentication.

**Get a token:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@jadeglobal.com", "password": "admin123"}'
```

**Use the token:**

```bash
curl http://localhost:8000/api/v1/providers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Key Endpoints

#### Authentication
```
POST   /api/v1/auth/login       # Login and get JWT token
POST   /api/v1/auth/register    # Register new user (admin only)
GET    /api/v1/auth/me          # Get current user info
```

#### Providers & Pricing
```
GET    /api/v1/providers                      # List providers
GET    /api/v1/providers/{id}/regions         # List regions
GET    /api/v1/pricing/compute                # Get compute pricing
GET    /api/v1/pricing/storage                # Get storage pricing
GET    /api/v1/reserved/pricing               # Get reserved pricing
GET    /api/v1/kubernetes/pricing             # Get Kubernetes pricing
GET    /api/v1/network/pricing                # Get network pricing
```

#### Calculations
```
POST   /api/v1/calculations                   # Create standard calculation
POST   /api/v1/reserved/calculate             # Calculate reserved instances
POST   /api/v1/kubernetes/calculate           # Calculate Kubernetes costs
POST   /api/v1/network/calculate              # Calculate network costs
GET    /api/v1/calculations                   # Get calculation history
GET    /api/v1/calculations/{id}              # Get single calculation
DELETE /api/v1/calculations/{id}              # Delete calculation
```

#### Budgets
```
GET    /api/v1/budgets                        # List budgets
POST   /api/v1/budgets                        # Create budget
PUT    /api/v1/budgets/{id}                   # Update budget
DELETE /api/v1/budgets/{id}                   # Delete budget
GET    /api/v1/budgets/{id}/alerts            # Get budget alerts
PUT    /api/v1/budgets/alerts/{id}            # Update alert status
```

#### AI Recommendations
```
POST   /api/v1/recommendations/generate       # Generate AI recommendations
GET    /api/v1/recommendations/history        # View past recommendations
```

#### Export
```
GET    /api/v1/export/calculations/{id}/pdf   # Export calculation as PDF
GET    /api/v1/export/calculations/{id}/excel # Export calculation as Excel
```

#### Admin (admin role required)
```
GET    /api/v1/admin/users                    # List all users
POST   /api/v1/admin/users                    # Create user
PUT    /api/v1/admin/users/{id}               # Update user
DELETE /api/v1/admin/users/{id}               # Delete user
GET    /api/v1/admin/audit-logs               # View audit logs
GET    /api/v1/admin/stats                    # Platform statistics
POST   /api/v1/admin/ingest                   # Trigger pricing ingestion
```

---

## Database Schema

### Core Tables

- **users** — User accounts with roles
- **providers** — Cloud providers (AWS, Azure, GCP)
- **regions** — Cloud regions per provider

### Pricing Tables

- **compute_pricing** — VM/EC2/Compute Engine pricing
- **storage_pricing** — Block & object storage pricing
- **reserved_pricing** — Reserved instance plans
- **kubernetes_pricing** — Managed Kubernetes pricing
- **network_pricing** — Data transfer pricing

### Application Tables

- **calculations** — Calculation history with full input/output
- **budgets** — Budget definitions
- **budget_alerts** — Budget alert events
- **audit_logs** — Complete audit trail

---

## Pricing Ingestion

The system automatically ingests latest pricing data daily at 2:00 AM UTC.

### Strategy

1. **Primary**: Live API calls to AWS, Azure, GCP pricing APIs
2. **Fallback**: Comprehensive hardcoded pricing data (always available)
3. **Upsert Logic**: Updates existing prices, inserts new ones (idempotent)

### Manual Trigger

Admins can trigger immediate ingestion:

```bash
curl -X POST http://localhost:8000/api/v1/admin/ingest \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

Or via the Admin Dashboard UI.

---

## AI Recommendations

The AI recommendations engine uses **Claude Sonnet 4** (claude-sonnet-4-20250514) to analyze calculation patterns and suggest cost optimizations.

### Configuration

Set your Anthropic API key in `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get an API key at: https://console.anthropic.com/

### How It Works

1. User selects 1-10 calculations to analyze
2. System builds structured context with all cost data
3. Claude analyzes patterns and generates recommendations
4. Returns actionable insights with estimated savings

### Recommendation Categories

- Cost Reduction
- Reserved Instances
- Right-Sizing
- Region Optimization
- Storage Optimization
- Kubernetes Optimization

---

## Security

### Password Hashing

- **bcrypt** with automatic salt generation
- Cost factor: 12 (configurable in `security.py`)

### JWT Tokens

- **Algorithm**: HS256
- **Expiry**: 24 hours (configurable)
- **Payload**: `{userId, email, role}` (camelCase for frontend compatibility)

### CORS

Configured in `main.py` to allow requests from frontend origins:

```python
allow_origins=settings.CORS_ORIGINS  # from .env
```

---

## Audit Logging

All significant actions are logged to `audit_logs` table:

- User authentication (login, logout)
- Calculations created
- Budgets created/updated/deleted
- AI recommendations generated
- Exports created
- Admin actions (user CRUD, manual ingestion)

Logs include:
- User ID and email
- Action type
- Input data (JSON)
- Success/failure status
- Error messages (if failed)
- IP address
- Timestamp

---

## Testing

Run backend server and test key endpoints:

```bash
# Health check
curl http://localhost:8000/api/healthz

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@jadeglobal.com", "password": "admin123"}'

# Get providers (requires token from login)
curl http://localhost:8000/api/v1/providers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Performance Considerations

- **Async operations** throughout for I/O-bound tasks
- **Database indexes** on frequently queried columns
- **Query optimization** with SQLAlchemy relationship loading strategies
- **Pagination** on all list endpoints
- **Connection pooling** via SQLAlchemy engine

---

## Maintenance

### Database Backup

```bash
# Backup
pg_dump jade_db > backup_$(date +%Y%m%d).sql

# Restore
psql jade_db < backup_20250101.sql
```

### Logs

Application logs are written to stdout. Redirect to file:

```bash
uvicorn app.main:app > app.log 2>&1
```

### Monitoring

Check application health:

```bash
curl http://localhost:8000/api/healthz
```

Admin stats dashboard provides platform usage metrics.

---

## License

Proprietary — Jade Global Software Pvt Ltd. All rights reserved.
