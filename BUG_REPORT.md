# Bug Report and Fixes

## Bug #1: SQL Injection Vulnerability (CRITICAL SECURITY ISSUE)

### Location
`app.py`, lines 25-33 (login function)

### Description
The login endpoint is vulnerable to SQL injection attacks. User input (`username` and `password`) is directly concatenated into the SQL query string without any sanitization or parameterization.

### Impact
- **Severity**: CRITICAL
- An attacker can bypass authentication by injecting SQL code
- Example attack: username = `admin' OR '1'='1' --` would bypass login
- Potential for data extraction, modification, or deletion
- Complete database compromise possible

### Attack Example
```
POST /login
username: admin' OR '1'='1' --
password: anything

The resulting query becomes:
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = 'anything'

The -- comments out the rest, and '1'='1' is always true, bypassing authentication.
```

### Fix
Use parameterized queries (prepared statements) instead of string concatenation.

---

## Bug #2: Logic Error - Off-by-One Array Indexing

### Location
`app.py`, lines 37-52 (get_user_data function)

### Description
The function has an off-by-one error when accessing the user_cache array. It uses `user_id` directly as the array index instead of `user_id - 1`. Since user IDs start at 1 but array indices start at 0, this causes:
- user_id=1 returns the wrong user (Bob instead of Alice)
- user_id=5 returns None and causes IndexError
- user_id=6 would cause IndexError instead of returning "User not found"

### Impact
- **Severity**: HIGH
- Returns incorrect user data
- Can cause application crashes with IndexError
- Logic errors affect all API consumers

### Example
```
Request: GET /get_user_data/1
Expected: {"id": 1, "name": "Alice", "role": "admin"}
Actual: {"id": 2, "name": "Bob", "role": "user"}
```

### Fix
Change `user_cache[user_id]` to `user_cache[user_id - 1]` and adjust boundary check.

---

## Bug #3: Performance Issues - N+1 Query Problem

### Location
`app.py`, lines 55-84 (calculate_stats function)

### Description
Multiple performance issues in the calculate_stats endpoint:

1. **N+1 Query Problem**: 
   - First queries all user IDs
   - Then makes N separate queries (one per user) to fetch user details
   - Should fetch all user data in a single query

2. **Unnecessary Computation**:
   - Hashes the username 1000 times using MD5 in a loop
   - This serves no purpose and wastes CPU cycles

3. **String Formatting in SQL**:
   - Uses f-string in the loop query (also a minor SQL injection risk)

### Impact
- **Severity**: MEDIUM to HIGH
- With 100 users: 101 database queries instead of 1
- With 1000 users: 1001 queries + 1,000,000 MD5 hash operations
- Response time scales poorly with user count
- High CPU and database load
- Poor user experience

### Performance Comparison
```
Current: O(N) queries + O(N * 1000) hash operations
Fixed: O(1) queries + O(N) hash operations

For 1000 users:
- Current: ~1001 queries + 1,000,000 hashes
- Fixed: 1 query + 1,000 hashes (1000x improvement)
```

### Fix
1. Use a single JOIN or single query to fetch all data
2. Remove unnecessary hashing loop
3. Use parameterized queries

---

## Bonus Bug #4: XSS Vulnerability (Security Issue)

### Location
`app.py`, lines 87-98 (profile function)

### Description
Cross-Site Scripting (XSS) vulnerability where user input is directly inserted into HTML without escaping.

### Impact
- **Severity**: HIGH
- Attackers can inject malicious JavaScript
- Can steal cookies, session tokens, or perform actions as the victim

### Attack Example
```
GET /profile/<script>alert('XSS')</script>

This would execute JavaScript in the victim's browser.
```

### Fix
Use Flask's automatic escaping or explicitly escape user input.
