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
from app.models.user import User, UserRole
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
        
        from sqlalchemy import select
        
        # Create providers (skip if exist)
        providers_map = {}
        for provider_name in PROVIDERS:
            result = await db.execute(select(Provider).where(Provider.name == provider_name))
            existing = result.scalar_one_or_none()
            if existing:
                providers_map[provider_name] = existing
                print(f"✓ Provider already exists: {provider_name}")
            else:
                provider = Provider(name=provider_name)
                db.add(provider)
                await db.flush()
                providers_map[provider_name] = provider
                print(f"✓ Created provider: {provider_name}")
        
        await db.commit()
        
        # Create regions (skip if exist)
        region_count = 0
        for region_code, region_name in AWS_REGIONS:
            result = await db.execute(select(Region).where(Region.region_code == region_code))
            if not result.scalar_one_or_none():
                region = Region(
                    provider_id=providers_map["AWS"].id,
                    region_code=region_code,
                    region_name=region_name,
                )
                db.add(region)
                region_count += 1
        
        for region_code, region_name in AZURE_REGIONS:
            result = await db.execute(select(Region).where(Region.region_code == region_code))
            if not result.scalar_one_or_none():
                region = Region(
                    provider_id=providers_map["Azure"].id,
                    region_code=region_code,
                    region_name=region_name,
                )
                db.add(region)
                region_count += 1
        
        for region_code, region_name in GCP_REGIONS:
            result = await db.execute(select(Region).where(Region.region_code == region_code))
            if not result.scalar_one_or_none():
                region = Region(
                    provider_id=providers_map["GCP"].id,
                    region_code=region_code,
                    region_name=region_name,
                )
                db.add(region)
                region_count += 1
        
        await db.commit()
        if region_count > 0:
            print(f"✓ Created {region_count} regions")
        else:
            print(f"✓ Regions already exist")
        
        # Create users (skip if exist)
        for user_data in USERS:
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            if result.scalar_one_or_none():
                print(f"✓ User already exists: {user_data['email']} ({user_data['role']})")
            else:
                user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=UserRole(user_data["role"]),
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
