#!/usr/bin/env python3
"""
Test script to verify the backend setup
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection"""
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_llm_service():
    """Test LLM service initialization"""
    try:
        from app.llm_service import LLMService
        llm = LLMService()
        print("✅ LLM service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ LLM service initialization failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint"""
    base_url = "http://localhost:8000"
    
    try:
        # Test chat endpoint
        payload = {
            "message": "Hello, can you help me find some shirts?",
            "user_id": 1
        }
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            print(f"   Session ID: {data.get('session_id', 'No session ID')}")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def check_environment():
    """Check environment variables"""
    required_vars = ["DATABASE_URL", "GROQ_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return False
    else:
        print("✅ Environment variables configured")
        return True

def main():
    """Run all tests"""
    print("🧪 Testing E-commerce Chatbot Backend Setup")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", check_environment),
        ("Database Connection", test_database_connection),
        ("LLM Service", test_llm_service),
        ("API Endpoints", test_api_endpoints),
        ("Chat Endpoint", test_chat_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Start the server: python run.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Test the chat functionality")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure PostgreSQL is running")
        print("   2. Check your .env file configuration")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Load data: python scripts/load_data.py")

if __name__ == "__main__":
    main() 