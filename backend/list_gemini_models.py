#!/usr/bin/env python3
"""List available Gemini models"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings
import google.generativeai as genai

print("=" * 60)
print("LISTING AVAILABLE GEMINI MODELS")
print("=" * 60)

api_key = settings.GOOGLE_API_KEY
print(f"\nAPI Key: {api_key[:20]}...")

print("\nConfiguring Gemini...")
genai.configure(api_key=api_key)

print("\nAvailable models:")
print("-" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Display name: {model.display_name}")
            print(f"  Description: {model.description[:100]}..." if len(model.description) > 100 else f"  Description: {model.description}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
    sys.exit(1)
