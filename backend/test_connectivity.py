#!/usr/bin/env python3
"""Test connectivity between frontend, backend, and database."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def test_connectivity():
    """Test all connections."""
    print("=" * 60)
    print("CONNECTIVITY TEST")
    print("=" * 60)

    # Test 1: Database connection
    print("\n[1/3] Testing Database Connection...")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Test 2: Backend Health Endpoint
    print("\n[2/3] Testing Backend Health Endpoint...")
    import subprocess

    tests = [
        ("localhost:8000", "curl -s http://localhost:8000/api/healthz"),
        ("0.0.0.0:8000", "curl -s http://0.0.0.0:8000/api/healthz"),
        ("192.168.10.200:8000", "curl -s http://192.168.10.200:8000/api/healthz"),
    ]

    for name, cmd in tests:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and "ok" in result.stdout:
                print(f"✅ Backend accessible on {name}")
            else:
                print(f"❌ Backend not accessible on {name}: {result.stderr}")
        except Exception as e:
            print(f"❌ Backend not accessible on {name}: {e}")

    # Test 3: Backend Login Endpoint
    print("\n[3/3] Testing Backend Login Endpoint...")
    login_tests = [
        ("localhost:8000", "curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@jadeglobal.com\",\"password\":\"admin123\"}'"),
        ("192.168.10.200:8000", "curl -s -X POST http://192.168.10.200:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@jadeglobal.com\",\"password\":\"admin123\"}'"),
    ]

    for name, cmd in login_tests:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and "token" in result.stdout:
                print(f"✅ Login works on {name}")
            else:
                print(f"❌ Login failed on {name}")
                if result.stdout:
                    print(f"   Response: {result.stdout[:200]}")
        except Exception as e:
            print(f"❌ Login test failed on {name}: {e}")

    # Test 4: Frontend Proxy
    print("\n[4/4] Testing Frontend Vite Proxy...")
    proxy_tests = [
        ("localhost:5173", "curl -s http://localhost:5173/api/healthz"),
        ("192.168.10.200:5173", "curl -s http://192.168.10.200:5173/api/healthz"),
    ]

    for name, cmd in proxy_tests:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and "ok" in result.stdout:
                print(f"✅ Vite proxy works on {name}")
            else:
                print(f"❌ Vite proxy not working on {name}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
        except Exception as e:
            print(f"❌ Vite proxy test failed on {name}: {e}")

    print("\n" + "=" * 60)
    print("NETWORK CONFIGURATION")
    print("=" * 60)

    # Show network info
    result = subprocess.run("hostname -I", shell=True, capture_output=True, text=True)
    print(f"Server IPs: {result.stdout.strip()}")

    result = subprocess.run("ps aux | grep -E '(uvicorn|vite)' | grep -v grep", shell=True, capture_output=True, text=True)
    print(f"\nRunning servers:\n{result.stdout}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\nIf all tests pass, the issue might be:")
    print("1. CORS headers not being properly sent")
    print("2. Vite proxy not forwarding requests correctly")
    print("3. Backend crashing on specific requests")
    print("\nPlease check the BACKEND TERMINAL (where uvicorn is running)")
    print("and look for ERROR messages when you try to login.")


if __name__ == "__main__":
    asyncio.run(test_connectivity())
