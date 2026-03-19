# JADE Cloud Matrix

**Cloud Pricing Intelligence Engine**  
_Jade Global Software Pvt Ltd — Infrastructure BU_

---

## Overview

JADE Cloud Matrix is an enterprise-grade full-stack application that enables intelligent multi-cloud pricing analysis and cost optimization across AWS, Azure, and GCP.

### Key Features

- 🔄 **Multi-Cloud Cost Comparison** — Compare compute, storage, reserved instances, Kubernetes, and network pricing across all major cloud providers
- 💰 **Budget Management** — Track spending, set alerts, and receive notifications when budgets are exceeded
- 🤖 **AI-Powered Recommendations** — Get intelligent cost optimization insights powered by Claude AI (Anthropic)
- 📊 **Comprehensive Reporting** — Export detailed pricing analysis as PDF or Excel
- 📈 **Historical Analysis** — Full calculation history with advanced filtering
- 🔐 **Role-Based Access Control** — Admin and user roles with different permissions
- ⏰ **Automated Price Updates** — Daily ingestion of latest cloud pricing data
- 🔍 **Audit Trail** — Complete logging of all user actions

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, React Router v6, TanStack Query v5 |
| **UI Framework** | shadcn/ui + Tailwind CSS v3 |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic |
| **Authentication** | JWT (python-jose) + bcrypt |
| **AI Engine** | Anthropic Claude API (claude-sonnet-4-20250514) |
| **Scheduling** | APScheduler |
| **Export** | ReportLab (PDF), openpyxl (Excel) |

---

## Project Structure

```
jade-cloud-matrix/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── api/       # API client modules
│   │   ├── components/ # React components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── pages/     # Page components
│   │   ├── types/     # TypeScript interfaces
│   │   └── lib/       # Utilities
│   └── package.json
│
└── backend/           # FastAPI backend
    ├── app/
    │   ├── routers/   # API endpoints (12 routers)
    │   ├── models/    # SQLAlchemy models (9 models)
    │   ├── schemas/   # Pydantic schemas (11 schemas)
    │   ├── services/  # Business logic
    │   └── core/      # Security & utilities
    ├── alembic/       # Database migrations
    ├── scripts/       # Utility scripts
    └── requirements.txt
```

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (with npm)
- **PostgreSQL 15+**
- **Anthropic API Key** (for AI recommendations)

### 1. Database Setup

```bash
# Install PostgreSQL 15 (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql-15 postgresql-contrib

# Create database and user
sudo -u postgres psql -f db_setup.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL (if different from default)
# - JWT_SECRET_KEY (generate a secure random string)
# - ANTHROPIC_API_KEY (your Claude API key)

# Run database migrations
alembic upgrade head

# Seed initial data (providers, regions, users, pricing)
python scripts/seed.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**  
API documentation at: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## Default Credentials

After running the seed script, these accounts are available:

| Role | Email | Password |
|---|---|---|
| **Admin** | admin@jadeglobal.com | admin123 |
| **User** | user@jadeglobal.com | user123 |

⚠️ **Change these passwords in production!**

---

## Environment Variables

See `.env.example` for all available configuration options.

### Required Variables

```env
DATABASE_URL=postgresql+asyncpg://jade_user:jade_pass@localhost:5432/jade_db
JWT_SECRET_KEY=change-this-to-a-random-32-char-minimum-string
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### Optional Variables

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` — For live AWS pricing (fallback data used if not provided)
- `AZURE_SUBSCRIPTION_ID` — For live Azure pricing
- `GCP_PROJECT_ID` — For live GCP pricing
- `INGESTION_HOUR`, `INGESTION_MINUTE` — Schedule for daily pricing updates (default: 2:00 AM UTC)

---

## Usage Guide

### 1. Standard Pricing Calculation

1. Navigate to **Calculator** page
2. Select **Standard** tab
3. Add compute instances (provider, region, instance type, quantity)
4. Add storage resources (provider, region, storage type, size)
5. Set duration in months
6. Click **Calculate Pricing**
7. View comparison results with charts
8. Export as PDF or Excel

### 2. Reserved Instance Analysis

1. Navigate to **Calculator** → **Reserved** tab
2. Select provider and region
3. Choose reserved instance plans (term, payment type)
4. Set quantity and duration
5. Calculate to see savings vs on-demand pricing

### 3. Kubernetes Cost Modeling

1. Navigate to **Calculator** → **Kubernetes** tab
2. Select provider, region, and node type
3. Set node count and duration
4. Toggle cluster management fee inclusion
5. Calculate total cluster costs

### 4. Budget Tracking

1. Navigate to **Budgets** page
2. Create a new budget with:
   - Name and optional provider filter
   - Budget amount and period (monthly/quarterly/annual)
   - Alert threshold (% of budget)
3. Monitor current spend automatically computed from calculations
4. Receive alerts when threshold is exceeded

### 5. AI Recommendations

1. Navigate to **AI Insights** page
2. Select up to 10 calculations to analyze
3. Click **Generate Recommendations**
4. Claude AI analyzes your usage patterns and suggests optimizations
5. View estimated savings and actionable steps

### 6. Admin Functions

Admins have access to:

- **User Management** — Create, edit, delete users
- **Audit Logs** — View complete system activity with filtering
- **System Stats** — Monitor platform usage metrics
- **Manual Ingestion** — Trigger immediate pricing data update

---

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI).

### Key Endpoints

```
POST   /api/v1/auth/login              # User authentication
GET    /api/v1/providers               # List cloud providers
GET    /api/v1/pricing/compute         # Get compute pricing
POST   /api/v1/calculations            # Create calculation
GET    /api/v1/calculations            # Get calculation history
POST   /api/v1/recommendations/generate # Get AI recommendations
GET    /api/v1/export/calculations/{id}/pdf   # Export as PDF
GET    /api/v1/admin/stats             # Admin statistics
```

---

## Architecture Notes

### Database

- **12 tables** with proper indexes and foreign keys
- **6 PostgreSQL enums** for type safety
- **Async SQLAlchemy** throughout for performance
- **Alembic migrations** for version control

### Authentication

- **JWT tokens** with configurable expiry (default: 24 hours)
- **bcrypt** for password hashing
- **Role-based access control** (admin vs user)
- Tokens automatically refreshed on API calls

### Pricing Ingestion

- **Primary strategy**: Live API calls to cloud provider pricing APIs
- **Fallback strategy**: Comprehensive hardcoded pricing data
- **Scheduled updates**: Daily at 2:00 AM UTC (configurable)
- **Manual trigger**: Available via admin panel

### AI Integration

- **Claude Sonnet 4** (claude-sonnet-4-20250514) via Anthropic API
- Analyzes up to 10 calculations simultaneously
- Provides category-based recommendations with priority levels
- Estimates monthly and annual savings potential

---

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload

# Create a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run tests (if added)
pytest
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -c "\l" | grep jade_db

# Check user permissions
sudo -u postgres psql -c "\du" | grep jade_user
```

### Backend Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

---

## Support

For issues or questions, contact the Jade Global Infrastructure BU team.

**Project:** JADE Cloud Matrix  
**Version:** 1.0.0  
**Client:** Jade Global Software Pvt Ltd — Infra BU  
**Built with:** FastAPI + React + PostgreSQL
