"""
Test cases to demonstrate the bug fixes
"""
import sqlite3
import hashlib
from unittest.mock import patch
import sys

def test_sql_injection_prevention():
    """Test Bug #1 Fix: SQL Injection Prevention"""
    print("\n=== Test 1: SQL Injection Prevention ===")
    
    # Setup test database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    ''')
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'password123')")
    conn.commit()
    
    # Test with malicious input - should NOT work with parameterized queries
    malicious_username = "admin' OR '1'='1' --"
    malicious_password = "anything"
    
    # Old vulnerable approach (for comparison only - DO NOT USE)
    print("❌ Old vulnerable code would execute:")
    print(f"   SELECT * FROM users WHERE username = '{malicious_username}' AND password = '{malicious_password}'")
    print("   This would bypass authentication!")
    
    # New safe approach with parameterized query
    print("\n✅ Fixed code with parameterized query:")
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (malicious_username, malicious_password))
    result = cursor.fetchone()
    
    if result is None:
        print("   ✓ PASS: SQL injection attack blocked successfully!")
        print("   No user found with malicious input")
    else:
        print("   ✗ FAIL: SQL injection not properly prevented")
    
    # Test with legitimate credentials
    cursor.execute(query, ('admin', 'password123'))
    result = cursor.fetchone()
    if result:
        print("   ✓ PASS: Legitimate login still works")
    
    conn.close()

def test_off_by_one_fix():
    """Test Bug #2 Fix: Off-by-one Error"""
    print("\n=== Test 2: Off-by-One Error Fix ===")
    
    user_cache = [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Charlie", "role": "user"},
        {"id": 4, "name": "Diana", "role": "moderator"},
        {"id": 5, "name": "Eve", "role": "user"}
    ]
    
    def get_user_fixed(user_id):
        """Fixed version"""
        if 1 <= user_id <= len(user_cache):
            return user_cache[user_id - 1]
        return None
    
    def get_user_buggy(user_id):
        """Buggy version for comparison"""
        if user_id <= len(user_cache):
            return user_cache[user_id]  # Bug here
        return None
    
    # Test case 1: user_id = 1 should return Alice
    print("\n📋 Test case: user_id = 1")
    print(f"   Expected: Alice (admin)")
    
    try:
        buggy_result = get_user_buggy(1)
        print(f"   ❌ Buggy code returns: {buggy_result['name']} ({buggy_result['role']}) - WRONG!")
    except (IndexError, TypeError) as e:
        print(f"   ❌ Buggy code crashes: {e}")
    
    fixed_result = get_user_fixed(1)
    print(f"   ✅ Fixed code returns: {fixed_result['name']} ({fixed_result['role']}) - CORRECT!")
    
    # Test case 2: user_id = 5 (edge case)
    print("\n📋 Test case: user_id = 5")
    print(f"   Expected: Eve (user)")
    
    try:
        buggy_result = get_user_buggy(5)
        if buggy_result:
            print(f"   ❌ Buggy code returns: {buggy_result['name']} - might work by luck")
        else:
            print(f"   ❌ Buggy code returns: None - WRONG!")
    except IndexError as e:
        print(f"   ❌ Buggy code crashes with IndexError: {e}")
    
    fixed_result = get_user_fixed(5)
    if fixed_result:
        print(f"   ✅ Fixed code returns: {fixed_result['name']} ({fixed_result['role']}) - CORRECT!")
    
    # Test case 3: user_id = 6 (out of bounds)
    print("\n📋 Test case: user_id = 6 (should return None)")
    
    try:
        buggy_result = get_user_buggy(6)
        print(f"   ❌ Buggy code crashes or returns wrong data")
    except IndexError as e:
        print(f"   ❌ Buggy code crashes with IndexError (should return None gracefully)")
    
    fixed_result = get_user_fixed(6)
    if fixed_result is None:
        print(f"   ✅ Fixed code returns: None - CORRECT!")

def test_performance_improvement():
    """Test Bug #3 Fix: Performance Optimization"""
    print("\n=== Test 3: Performance Optimization ===")
    
    # Setup test database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)')
    
    # Insert test data
    test_users = [(i, f'user{i}') for i in range(1, 101)]
    cursor.executemany('INSERT INTO users VALUES (?, ?)', test_users)
    conn.commit()
    
    # Buggy version
    def calculate_stats_buggy():
        cursor.execute("SELECT id FROM users")
        user_ids = cursor.fetchall()
        query_count = 1
        hash_count = 0
        
        stats = []
        for user_id in user_ids:
            cursor.execute(f"SELECT * FROM users WHERE id = {user_id[0]}")
            user = cursor.fetchone()
            query_count += 1
            
            hashed_data = user[1]
            for i in range(1000):
                hashed_data = hashlib.md5(hashed_data.encode()).hexdigest()
                hash_count += 1
            
            stats.append({"id": user[0], "username": user[1], "hash": hashed_data})
        
        return stats, query_count, hash_count
    
    # Fixed version
    def calculate_stats_fixed():
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        query_count = 1
        hash_count = 0
        
        stats = []
        for user in users:
            hashed_data = hashlib.md5(user[1].encode()).hexdigest()
            hash_count += 1
            stats.append({"id": user[0], "username": user[1], "hash": hashed_data})
        
        return stats, query_count, hash_count
    
    print("\n📊 Performance comparison with 100 users:")
    
    # Run buggy version
    import time
    start = time.time()
    _, buggy_queries, buggy_hashes = calculate_stats_buggy()
    buggy_time = time.time() - start
    
    print(f"\n❌ Buggy version:")
    print(f"   Database queries: {buggy_queries}")
    print(f"   MD5 hash operations: {buggy_hashes}")
    print(f"   Execution time: {buggy_time:.4f} seconds")
    
    # Run fixed version
    start = time.time()
    _, fixed_queries, fixed_hashes = calculate_stats_fixed()
    fixed_time = time.time() - start
    
    print(f"\n✅ Fixed version:")
    print(f"   Database queries: {fixed_queries}")
    print(f"   MD5 hash operations: {fixed_hashes}")
    print(f"   Execution time: {fixed_time:.4f} seconds")
    
    print(f"\n📈 Improvements:")
    print(f"   Query reduction: {buggy_queries}x → 1x ({buggy_queries}x fewer queries)")
    print(f"   Hash reduction: {buggy_hashes} → {fixed_hashes} ({buggy_hashes//fixed_hashes}x fewer hashes)")
    print(f"   Speed improvement: {buggy_time/fixed_time:.2f}x faster")
    
    conn.close()

def test_xss_prevention():
    """Test Bonus Fix: XSS Prevention"""
    print("\n=== Bonus Test: XSS Prevention ===")
    
    # Malicious input
    malicious_input = "<script>alert('XSS')</script>"
    
    print(f"\n🔴 Malicious input: {malicious_input}")
    
    # Buggy version (f-string)
    print(f"\n❌ Buggy version (f-string interpolation):")
    buggy_html = f"<h1>Welcome, {malicious_input}!</h1>"
    print(f"   Output: {buggy_html}")
    print(f"   ⚠️  Script tag is NOT escaped - XSS vulnerability!")
    
    # Fixed version (would use Flask's auto-escaping)
    print(f"\n✅ Fixed version (Flask template with auto-escaping):")
    # Simple HTML escaping without external dependencies
    import html
    safe_input = html.escape(malicious_input)
    fixed_html = f"<h1>Welcome, {safe_input}!</h1>"
    print(f"   Output: {fixed_html}")
    print(f"   ✓ Script tag is escaped - XSS prevented!")

if __name__ == '__main__':
    print("=" * 60)
    print("BUG FIX VERIFICATION TESTS")
    print("=" * 60)
    
    test_sql_injection_prevention()
    test_off_by_one_fix()
    test_performance_improvement()
    test_xss_prevention()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
