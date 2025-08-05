#!/usr/bin/env python3
"""
Test script for the Flask application endpoints
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get('http://localhost:8080/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_main_page():
    """Test the main page loads"""
    print("\nTesting main page...")
    try:
        response = requests.get('http://localhost:8080/')
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            return True
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Main page error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat API endpoint"""
    print("\nTesting chat endpoint...")
    try:
        data = {
            "message": "Hallo, können Sie mir mehr über Botox-Behandlungen erzählen?"
        }
        headers = {
            "Content-Type": "application/json",
            "X-Session-ID": "test_session_123"
        }
        
        response = requests.post(
            'http://localhost:8080/api/chat',
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint working")
            print(f"Response: {result.get('message', 'No message')[:100]}...")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 Testing Haut Labor Chatbot Flask Application")
    print("=" * 50)
    
    # Wait a moment for the app to be ready
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_main_page,
        test_chat_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Flask app is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the Flask app configuration.")

if __name__ == "__main__":
    main() 