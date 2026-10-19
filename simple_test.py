"""Simple API test"""
import requests

print("Testing backend API...")

# Test 1: Get profile
print("\n1. GET /auth/me")
try:
    r = requests.get("http://localhost:8000/auth/me", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Register user
print("\n2. POST /auth/register")
try:
    data = {"username": "test123", "password": "pass123"}
    r = requests.post("http://localhost:8000/auth/register", json=data, timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Create post
print("\n3. POST /posts")
try:
    data = {
        "title": "Test Post",
        "text": "This is a test",
        "category": "ride_report"
    }
    r = requests.post("http://localhost:8000/posts", json=data, timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Get posts
print("\n4. GET /posts")
try:
    r = requests.get("http://localhost:8000/posts?limit=5", timeout=5)
    print(f"   Status: {r.status_code}")
    posts = r.json()
    print(f"   Posts count: {len(posts)}")
    if posts:
        print(f"   First post: {posts[0]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Add bike
print("\n5. POST /bikes")
try:
    data = {
        "brand": "Specialized",
        "model": "Stumpjumper",
        "year": 2024
    }
    r = requests.post("http://localhost:8000/bikes", json=data, timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 6: Get bikes
print("\n6. GET /bikes/my-bikes")
try:
    r = requests.get("http://localhost:8000/bikes/my-bikes", timeout=5)
    print(f"   Status: {r.status_code}")
    bikes = r.json()
    print(f"   Bikes count: {len(bikes)}")
    if bikes:
        print(f"   Bikes: {bikes}")
except Exception as e:
    print(f"   Error: {e}")

print("\n✅ Test completed!")
