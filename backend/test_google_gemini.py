#!/usr/bin/env python3
"""Test script to verify Google Gemini API configuration"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
import google.generativeai as genai

print("=" * 60)
print("GOOGLE GEMINI API CONFIGURATION TEST")
print("=" * 60)

# Check if API key is loaded
api_key = settings.GOOGLE_API_KEY
print(f"\n1. API Key loaded: {'✓ Yes' if api_key else '✗ No'}")
print(f"   API Key length: {len(api_key)}")
print(f"   API Key starts with: {api_key[:20]}..." if len(api_key) > 20 else f"   API Key: {api_key}")

# Check for placeholder key
if api_key.startswith("your-google-api-key"):
    print("   ✗ WARNING: Using placeholder API key")
else:
    print("   ✓ Not a placeholder key")

# Try to configure Gemini
print("\n2. Configuring Google Gemini...")
try:
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel('gemini-2.5-flash')
    print("   ✓ Gemini configured successfully")
except Exception as e:
    print(f"   ✗ Failed to configure Gemini: {e}")
    sys.exit(1)

# Try a simple API call
print("\n3. Testing API connection with a simple call...")
try:
    response = client.generate_content("Say 'API test successful' and nothing else.")

    response_text = ""
    if hasattr(response, 'text'):
        response_text = response.text

    print(f"   ✓ API call successful!")
    print(f"   Response: {response_text}")

except Exception as e:
    print(f"   ✗ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - GOOGLE GEMINI API IS WORKING!")
print("=" * 60)
