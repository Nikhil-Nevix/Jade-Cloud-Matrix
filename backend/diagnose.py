#!/usr/bin/env python3
"""Quick diagnostic to check database state and test login."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import verify_password
from sqlalchemy import select


async def diagnose():
    """Run diagnostics."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("JADE Cloud Matrix - Login Diagnostics")
        print("=" * 60)

        # Check users
        result = await db.execute(select(User))
        users = result.scalars().all()

        print(f"\n📊 Total users in database: {len(users)}")

        if len(users) == 0:
            print("\n❌ NO USERS FOUND!")
            print("   Run: python fix_users.py")
            return

        print("\n👥 User Details:")
        for user in users:
            print(f"\n   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Role Type: {type(user.role)}")
            print(f"   Role Value: {user.role.value if hasattr(user.role, 'value') else 'NO VALUE ATTR'}")

            # Test password
            if user.email == "admin@jadeglobal.com":
                is_valid = verify_password("admin123", user.password_hash)
                print(f"   Password 'admin123' valid: {is_valid}")

                if not is_valid:
                    print("   ❌ PASSWORD VERIFICATION FAILED!")
                else:
                    print("   ✅ Password verification successful")

            # Check if role is proper enum
            if isinstance(user.role, UserRole):
                print("   ✅ Role is proper UserRole enum")
            else:
                print(f"   ❌ Role is NOT UserRole enum (it's {type(user.role).__name__})")
                print("      This will cause login to fail!")

        print("\n" + "=" * 60)
        print("RECOMMENDATION:")
        print("=" * 60)

        # Check if admin user exists and is valid
        result = await db.execute(select(User).where(User.email == "admin@jadeglobal.com"))
        admin = result.scalar_one_or_none()

        if not admin:
            print("❌ Admin user not found. Run: python fix_users.py")
        elif not isinstance(admin.role, UserRole):
            print("❌ Admin user role is not a proper enum. Run: python fix_users.py")
        elif not verify_password("admin123", admin.password_hash):
            print("❌ Admin password is incorrect. Run: python fix_users.py")
        else:
            print("✅ Admin user looks good!")
            print(f"\n   Login credentials:")
            print(f"   Email: {admin.email}")
            print(f"   Password: admin123")
            print(f"\n   Try logging in now at: http://192.168.10.200:5173/login")


if __name__ == "__main__":
    asyncio.run(diagnose())
