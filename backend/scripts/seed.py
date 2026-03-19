"""
Database seed script for JADE Cloud Matrix.
Run after Alembic migration to populate initial data.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.provider import Provider, Region
from app.models.user import User
from app.core.security import hash_password
from app.services.ingestion.runner import run_full_ingestion


USERS = [
    {"email": "admin@jadeglobal.com", "password": "admin123", "role": "admin"},
    {"email": "user@jadeglobal.com", "password": "user123", "role": "user"},
]

PROVIDERS = ["AWS", "Azure", "GCP"]

AWS_REGIONS = [
    ("us-east-1", "US East (N. Virginia)"),
    ("us-west-2", "US West (Oregon)"),
    ("eu-west-1", "Europe (Ireland)"),
    ("ap-south-1", "Asia Pacific (Mumbai)"),
    ("ap-southeast-1", "Asia Pacific (Singapore)"),
]

AZURE_REGIONS = [
    ("eastus", "East US"),
    ("westus2", "West US 2"),
    ("westeurope", "West Europe"),
    ("southeastasia", "Southeast Asia"),
    ("centralindia", "Central India"),
]

GCP_REGIONS = [
    ("us-east1", "US East (S. Carolina)"),
    ("us-west1", "US West (Oregon)"),
    ("europe-west1", "Europe West (Belgium)"),
    ("asia-south1", "Asia South (Mumbai)"),
    ("asia-southeast1", "Asia Southeast (Singapore)"),
]


async def seed_database():
    """Seed the database with initial data."""
    async with AsyncSessionLocal() as db:
        print("Starting database seed...")
        
        # Create providers
        providers_map = {}
        for provider_name in PROVIDERS:
            provider = Provider(name=provider_name)
            db.add(provider)
            await db.flush()
            providers_map[provider_name] = provider
            print(f"✓ Created provider: {provider_name}")
        
        await db.commit()
        
        # Create regions
        for region_code, region_name in AWS_REGIONS:
            region = Region(
                provider_id=providers_map["AWS"].id,
                region_code=region_code,
                region_name=region_name,
            )
            db.add(region)
        
        for region_code, region_name in AZURE_REGIONS:
            region = Region(
                provider_id=providers_map["Azure"].id,
                region_code=region_code,
                region_name=region_name,
            )
            db.add(region)
        
        for region_code, region_name in GCP_REGIONS:
            region = Region(
                provider_id=providers_map["GCP"].id,
                region_code=region_code,
                region_name=region_name,
            )
            db.add(region)
        
        await db.commit()
        print(f"✓ Created {len(AWS_REGIONS) + len(AZURE_REGIONS) + len(GCP_REGIONS)} regions")
        
        # Create users
        for user_data in USERS:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
            print(f"✓ Created user: {user_data['email']} ({user_data['role']})")
        
        await db.commit()
        
        # Run initial pricing ingestion
        print("\nRunning initial pricing data ingestion...")
        await run_full_ingestion(db)
        print("✓ Pricing data ingestion completed")
        
        print("\n" + "="*60)
        print("Database seeded successfully!")
        print("="*60)
        print("\nDefault Users:")
        print("  Admin: admin@jadeglobal.com / admin123")
        print("  User:  user@jadeglobal.com  / user123")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env and configure")
        print("  2. Start backend: cd backend && uvicorn app.main:app --reload")
        print("  3. Start frontend: cd frontend && npm run dev")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_database())
