"""
Simple web application with intentional bugs for demonstration
"""
import sqlite3
from flask import Flask, request, jsonify, render_template_string
import hashlib

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Bug #1 FIXED: Using parameterized queries to prevent SQL injection
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Fixed: Use parameterized query with ? placeholders
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Parameterized query - user input is safely escaped
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

# Bug #2 FIXED: Corrected off-by-one error in array indexing
@app.route('/get_user_data/<int:user_id>')
def get_user_data(user_id):
    """Get user data by ID from cache"""
    # Simulated user cache
    user_cache = [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Charlie", "role": "user"},
        {"id": 4, "name": "Diana", "role": "moderator"},
        {"id": 5, "name": "Eve", "role": "user"}
    ]
    
    # Fixed: Convert 1-based user_id to 0-based array index
    # Also fixed boundary check to use < instead of <=
    if 1 <= user_id <= len(user_cache):
        return jsonify(user_cache[user_id - 1])
    return jsonify({"error": "User not found"}), 404

# Bug #3 FIXED: Resolved N+1 query problem and removed unnecessary computation
@app.route('/calculate_stats')
def calculate_stats():
    """Calculate statistics for all users - optimized version"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fixed: Single query to fetch all user data at once (eliminates N+1 problem)
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    
    stats = []
    # Process all users with a single hash computation per user
    for user in users:
        # Fixed: Hash only once instead of 1000 times
        hashed_data = hashlib.md5(user[1].encode()).hexdigest()
        
        stats.append({
            "id": user[0],
            "username": user[1],
            "hash": hashed_data
        })
    
    conn.close()
    return jsonify(stats)

# BONUS FIX: XSS vulnerability fixed with proper escaping
@app.route('/profile/<username>')
def profile(username):
    # Fixed: Using Flask's template system which auto-escapes variables
    html = """
    <html>
    <head><title>User Profile</title></head>
    <body>
        <h1>Welcome, {{ username }}!</h1>
        <p>This is your profile page.</p>
    </body>
    </html>
    """
    # render_template_string with {{ }} notation automatically escapes variables
    return render_template_string(html, username=username)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
