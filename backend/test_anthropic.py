#!/usr/bin/env python3
"""Test script to verify Anthropic API configuration"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
from anthropic import Anthropic

print("=" * 60)
print("ANTHROPIC API CONFIGURATION TEST")
print("=" * 60)

# Check if API key is loaded
api_key = settings.ANTHROPIC_API_KEY
print(f"\n1. API Key loaded: {'✓ Yes' if api_key else '✗ No'}")
print(f"   API Key length: {len(api_key)}")
print(f"   API Key starts with: {api_key[:20]}..." if len(api_key) > 20 else f"   API Key: {api_key}")

# Check for placeholder key
if api_key.startswith("sk-ant-your-key"):
    print("   ✗ WARNING: Using placeholder API key")
else:
    print("   ✓ Not a placeholder key")

# Try to initialize client
print("\n2. Initializing Anthropic client...")
try:
    client = Anthropic(api_key=api_key)
    print("   ✓ Client initialized successfully")
except Exception as e:
    print(f"   ✗ Failed to initialize client: {e}")
    sys.exit(1)

# Try a simple API call
print("\n3. Testing API connection with a simple call...")
try:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'API test successful' and nothing else."}]
    )

    response_text = ""
    if hasattr(message, 'content') and len(message.content) > 0:
        for block in message.content:
            if hasattr(block, 'type') and block.type == 'text':
                response_text = block.text
                break

    print(f"   ✓ API call successful!")
    print(f"   Response: {response_text}")

except Exception as e:
    print(f"   ✗ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - ANTHROPIC API IS CONFIGURED CORRECTLY")
print("=" * 60)
