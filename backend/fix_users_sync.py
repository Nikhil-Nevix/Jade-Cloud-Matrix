"""
Fix users using synchronous psycopg2 instead of async.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import bcrypt

    # Database connection parameters
    DB_PARAMS = {
        'host': 'localhost',
        'port': 5433,
        'database': 'jade_db',
        'user': 'jade_user',
        'password': 'jade_pass'
    }

    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def fix_users():
        """Fix users with proper roles."""
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Delete existing users
            cur.execute("DELETE FROM users")
            conn.commit()
            print("✓ Cleared existing users")

            # Insert new users with proper roles
            users = [
                ("admin@jadeglobal.com", hash_password("admin123"), "admin"),
                ("user@jadeglobal.com", hash_password("user123"), "user"),
            ]

            for email, password_hash, role in users:
                cur.execute(
                    "INSERT INTO users (email, password_hash, role, created_at) VALUES (%s, %s, %s, NOW())",
                    (email, password_hash, role)
                )
                print(f"✓ Created user: {email} (role: {role})")

            conn.commit()

            # Verify
            cur.execute("SELECT email, role FROM users")
            users_in_db = cur.fetchall()
            print(f"\n✓ Total users in database: {len(users_in_db)}")
            for user in users_in_db:
                print(f"  - {user['email']}: role={user['role']}")

            print("\n✅ Users fixed successfully!")
            print("You can now login with:")
            print("  Admin: admin@jadeglobal.com / admin123")
            print("  User:  user@jadeglobal.com / user123")

        finally:
            cur.close()
            conn.close()

    if __name__ == "__main__":
        fix_users()

except ImportError as e:
    print(f"Error: Required module not found: {e}")
    print("Please install psycopg2-binary: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
