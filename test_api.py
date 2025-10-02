#!/usr/bin/env python3
"""
Test script for the AI Photo Restoration API
"""

import requests
import json
import base64
from PIL import Image
import io
import sys
import os

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get("http://localhost:7860/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_with_sample_image():
    """Test the API with a sample image"""
    print("\nTesting photo restoration API...")
    
    # Create a simple test image
    test_image = Image.new('RGB', (100, 100), color='gray')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    try:
        files = {'file': ('test.png', img_bytes.getvalue(), 'image/png')}
        data = {'restore_face': True, 'colorize': True}
        
        response = requests.post("http://localhost:7860/restore", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API test passed")
                print(f"📊 Response keys: {list(result.keys())}")
                return True
            else:
                print(f"❌ API test failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API test failed with status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running API tests...")
    print("=" * 50)
    
    # Test health check
    health_ok = test_health_check()
    
    # Test API
    api_ok = test_api_with_sample_image()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   API Test: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if health_ok and api_ok:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())