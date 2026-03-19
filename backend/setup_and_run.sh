#!/bin/bash
set -e

echo "🚀 JADE Cloud Matrix Backend Setup"
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Run migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Seed initial data
echo "🌱 Seeding database..."
python scripts/seed.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To start the backend server:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
