"""
Quick diagnostic script to test authentication issue.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import verify_password, hash_password
from sqlalchemy import select


async def test_auth():
    """Test authentication setup."""
    async with AsyncSessionLocal() as db:
        print("Testing authentication...")

        # Check if users exist
        result = await db.execute(select(User).where(User.email == "admin@jadeglobal.com"))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ Admin user not found in database!")
            return

        print(f"✓ User found: {user.email}")
        print(f"  Role: {user.role} (type: {type(user.role)})")
        print(f"  Password hash length: {len(user.password_hash)}")
        print(f"  Password hash starts with: {user.password_hash[:10]}...")

        # Test password verification
        test_password = "admin123"
        is_valid = verify_password(test_password, user.password_hash)
        print(f"\n✓ Password verification for '{test_password}': {is_valid}")

        if not is_valid:
            print("❌ Password verification failed!")
            print("  This means the stored hash doesn't match the expected password.")
            print("  Let's create a new hash to test:")
            new_hash = hash_password(test_password)
            print(f"  New hash: {new_hash[:50]}...")
            is_valid_new = verify_password(test_password, new_hash)
            print(f"  New hash verification: {is_valid_new}")
        else:
            print("✓ Password verification successful!")

        # Check role type
        if isinstance(user.role, UserRole):
            print(f"✓ Role is UserRole enum: {user.role.value}")
        elif isinstance(user.role, str):
            print(f"⚠️  Role is string, not enum: '{user.role}'")
            print("  This might cause issues with user.role.value")
        else:
            print(f"❌ Role has unexpected type: {type(user.role)}")


if __name__ == "__main__":
    asyncio.run(test_auth())
