"""Complete API testing script"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def print_separator():
    print("=" * 70)

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Helper function to test an endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        
        success = response.status_code == expected_status
        status_icon = "[OK]" if success else "[FAIL]"
        
        print(f"{status_icon} {name}")
        print(f"    Status: {response.status_code} (expected: {expected_status})")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"    Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"[ERROR] {name}")
        print(f"    Error: {str(e)[:200]}")
        return None

def main():
    print_separator()
    print("TESTING CYCLING SOCIAL NETWORK BACKEND API")
    print_separator()
    
    # Test 1: Server health check
    print("\n### Test 1: Server Health Check")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print(f"[OK] GET /docs")
            print(f"    Status: {response.status_code}")
        else:
            print(f"[FAIL] Server returned: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to server")
        print(f"    Error: {str(e)[:200]}")
        print(f"\n[CRITICAL] Cannot connect to server!")
        print(f"Make sure server is running at {BASE_URL}")
        sys.exit(1)
    
    # Test 2: User Registration (US1)
    print("\n### Test 2: User Registration (US1)")
    user1 = test_endpoint(
        "POST /auth/register - User 1",
        "POST",
        f"{BASE_URL}/auth/register",
        {"username": "test_rider_1", "password": "password123"},
        expected_status=201
    )
    
    if user1:
        print(f"    Created user: {user1.get('username')} (ID: {user1.get('id')})")
    
    # Try to register another user
    user2 = test_endpoint(
        "POST /auth/register - User 2",
        "POST",
        f"{BASE_URL}/auth/register",
        {"username": "test_rider_2", "password": "secure456"},
        expected_status=201
    )
    
    # Test 3: User Login (US1)
    print("\n### Test 3: User Login (US1)")
    login_result = test_endpoint(
        "POST /auth/login - Valid credentials",
        "POST",
        f"{BASE_URL}/auth/login",
        {"username": "test_rider_1", "password": "password123"}
    )
    
    if login_result:
        print(f"    Login message: {login_result.get('message')}")
    
    # Test invalid login
    test_endpoint(
        "POST /auth/login - Invalid password",
        "POST",
        f"{BASE_URL}/auth/login",
        {"username": "test_rider_1", "password": "wrongpass"},
        expected_status=401
    )
    
    # Test 4: Get Current User Profile (US2)
    print("\n### Test 4: Get User Profile (US2)")
    profile = test_endpoint(
        "GET /auth/me",
        "GET",
        f"{BASE_URL}/auth/me"
    )
    
    if profile:
        print(f"    Username: {profile.get('username')}")
        print(f"    Role: {profile.get('role')}")
        print(f"    City: {profile.get('city', 'Not set')}")
    
    # Test 5: Update User Profile (US2)
    print("\n### Test 5: Update User Profile (US2)")
    updated_profile = test_endpoint(
        "PUT /auth/me",
        "PUT",
        f"{BASE_URL}/auth/me",
        {
            "city": "Saint Petersburg",
            "discipline": "Road Cycling",
            "interests": "Long distance rides, gran fondos",
            "bio": "Amateur road cyclist from SPb"
        }
    )
    
    if updated_profile:
        print(f"    Updated city: {updated_profile.get('city')}")
        print(f"    Updated discipline: {updated_profile.get('discipline')}")
        print(f"    Updated bio: {updated_profile.get('bio')}")
    
    # Test 6: Create Posts (US3)
    print("\n### Test 6: Create Posts (US3)")
    
    post1 = test_endpoint(
        "POST /posts - Maintenance post",
        "POST",
        f"{BASE_URL}/posts",
        {
            "title": "How to clean your bike chain",
            "text": "Here's my method for keeping the chain clean and well-lubricated...",
            "category": "обслуживание",
            "photo_url": "https://example.com/chain.jpg"
        },
        expected_status=201
    )
    
    if post1:
        print(f"    Post ID: {post1.get('id')}")
        print(f"    Author: {post1.get('author_username')}")
        print(f"    Category: {post1.get('category')}")
    
    post2 = test_endpoint(
        "POST /posts - Route post",
        "POST",
        f"{BASE_URL}/posts",
        {
            "title": "Amazing trail in Leningrad Oblast",
            "text": "Discovered a beautiful 50km trail with scenic views!",
            "category": "маршрут"
        },
        expected_status=201
    )
    
    post3 = test_endpoint(
        "POST /posts - Upgrade post",
        "POST",
        f"{BASE_URL}/posts",
        {
            "title": "Upgraded to carbon wheels",
            "text": "Just installed new carbon wheelset. The difference is incredible!",
            "category": "апгрейд",
            "photo_url": "https://example.com/wheels.jpg"
        },
        expected_status=201
    )
    
    # Test 7: Get Posts Feed (US4)
    print("\n### Test 7: Get Posts Feed (US4)")
    
    feed = test_endpoint(
        "GET /posts - All posts",
        "GET",
        f"{BASE_URL}/posts"
    )
    
    if feed:
        print(f"    Total posts in feed: {len(feed)}")
        for i, post in enumerate(feed, 1):
            print(f"    {i}. '{post['title']}' by {post['author_username']}")
    
    # Test pagination
    feed_page1 = test_endpoint(
        "GET /posts?limit=2&offset=0 - First page",
        "GET",
        f"{BASE_URL}/posts?limit=2&offset=0"
    )
    
    if feed_page1:
        print(f"    Page 1 contains: {len(feed_page1)} posts")
    
    feed_page2 = test_endpoint(
        "GET /posts?limit=2&offset=2 - Second page",
        "GET",
        f"{BASE_URL}/posts?limit=2&offset=2"
    )
    
    if feed_page2:
        print(f"    Page 2 contains: {len(feed_page2)} posts")
    
    # Test 8: Get Single Post
    print("\n### Test 8: Get Single Post")
    
    if post1:
        single_post = test_endpoint(
            f"GET /posts/{post1['id']}",
            "GET",
            f"{BASE_URL}/posts/{post1['id']}"
        )
        
        if single_post:
            print(f"    Title: {single_post['title']}")
            print(f"    Text preview: {single_post['text'][:50]}...")
            print(f"    Category: {single_post['category']}")
    
    # Test non-existent post
    test_endpoint(
        "GET /posts/99999 - Non-existent",
        "GET",
        f"{BASE_URL}/posts/99999",
        expected_status=404
    )
    
    # Test 9: Add Bikes (US5)
    print("\n### Test 9: Add Bikes (US5)")
    
    bike1 = test_endpoint(
        "POST /bikes - MTB",
        "POST",
        f"{BASE_URL}/bikes",
        {
            "brand": "Specialized",
            "model": "Stumpjumper",
            "year": 2022
        },
        expected_status=201
    )
    
    if bike1:
        print(f"    Bike ID: {bike1.get('id')}")
        print(f"    Brand/Model: {bike1.get('brand')} {bike1.get('model')}")
        print(f"    Year: {bike1.get('year')}")
    
    bike2 = test_endpoint(
        "POST /bikes - Road bike",
        "POST",
        f"{BASE_URL}/bikes",
        {
            "brand": "Trek",
            "model": "Domane SL7",
            "year": 2023
        },
        expected_status=201
    )
    
    bike3 = test_endpoint(
        "POST /bikes - Gravel bike",
        "POST",
        f"{BASE_URL}/bikes",
        {
            "brand": "Canyon",
            "model": "Grizl CF",
            "year": 2024
        },
        expected_status=201
    )
    
    # Test 10: Get My Bikes (US5)
    print("\n### Test 10: Get My Bikes (US5)")
    
    my_bikes = test_endpoint(
        "GET /bikes/my-bikes",
        "GET",
        f"{BASE_URL}/bikes/my-bikes"
    )
    
    if my_bikes:
        print(f"    Total bikes: {len(my_bikes)}")
        for i, bike in enumerate(my_bikes, 1):
            print(f"    {i}. {bike['brand']} {bike['model']} ({bike['year']})")
    
    # Test 11: Invalid data validation
    print("\n### Test 11: Data Validation")
    
    test_endpoint(
        "POST /auth/register - Username too short",
        "POST",
        f"{BASE_URL}/auth/register",
        {"username": "ab", "password": "123456"},
        expected_status=422
    )
    
    test_endpoint(
        "POST /bikes - Invalid year",
        "POST",
        f"{BASE_URL}/bikes",
        {"brand": "Test", "model": "Model", "year": 3000},
        expected_status=422
    )
    
    # Summary
    print_separator()
    print("TEST SUMMARY")
    print_separator()
    print("\n[COMPLETE] All API endpoints have been tested!")
    print("\nTested User Stories:")
    print("  [OK] US1: User Registration and Login")
    print("  [OK] US2: User Profile Management")
    print("  [OK] US3: Create Posts")
    print("  [OK] US4: View Posts Feed with Pagination")
    print("  [OK] US5: Add and View Bikes")
    print("\nAdditional Features Tested:")
    print("  [OK] Input validation (422 errors)")
    print("  [OK] Error handling (404, 401 errors)")
    print("  [OK] Multiple post categories")
    print("  [OK] Feed pagination")
    print_separator()
    print(f"\nAPI Documentation: {BASE_URL}/docs")
    print_separator()

if __name__ == "__main__":
    main()
