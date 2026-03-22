"""
Fix existing users in the database to ensure roles are properly set.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select, delete


async def fix_users():
    """Fix or recreate users with proper role enums."""
    async with AsyncSessionLocal() as db:
        print("Fixing user data...")

        # Delete all existing users to recreate them properly
        await db.execute(delete(User))
        await db.commit()
        print("✓ Cleared existing users")

        # Recreate users with proper enum roles
        users_data = [
            {"email": "admin@jadeglobal.com", "password": "admin123", "role": UserRole.admin},
            {"email": "user@jadeglobal.com", "password": "user123", "role": UserRole.user},
        ]

        for user_data in users_data:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
            print(f"✓ Created user: {user_data['email']} (role: {user_data['role'].value})")

        await db.commit()

        # Verify users were created correctly
        result = await db.execute(select(User))
        users = result.scalars().all()

        print(f"\n✓ Total users in database: {len(users)}")
        for user in users:
            print(f"  - {user.email}: role={user.role} (type: {type(user.role).__name__})")

        print("\n✅ Users fixed successfully!")
        print("You can now login with:")
        print("  Admin: admin@jadeglobal.com / admin123")
        print("  User:  user@jadeglobal.com / user123")


if __name__ == "__main__":
    asyncio.run(fix_users())
