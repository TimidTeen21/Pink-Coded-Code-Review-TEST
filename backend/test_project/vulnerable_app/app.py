from flask import Flask, render_template, request, redirect, url_for, session, make_response
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'insecure_secret_key_123'  # Insecure secret key

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            balance INTEGER DEFAULT 1000
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content TEXT
        )
    ''')
    # Add some test data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      ('admin', 'insecure_password'))
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      ('user1', 'password1'))
        cursor.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", 
                      (1, 'Admin post with <script>alert(1)</script>'))
    conn.commit()
    conn.close()

init_db()

# Weak password hashing
def weak_hash(password):
    return hashlib.md5(password.encode()).hexdigest()  # Insecure hashing

@app.route('/')
def index():
    username = session.get('username', None)
    return render_template('index.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SQL Injection vulnerable query
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{weak_hash(password)}'")
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            return "Login failed", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    results = []
    if request.method == 'POST':
        query = request.form['query']
        
        # SQL Injection vulnerable
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM posts WHERE content LIKE '%{query}%'")
        results = cursor.fetchall()
        conn.close()
    
    return render_template('search.html', results=results)

@app.route('/profile/<username>')
def profile(username):
    # XSS vulnerable - username not escaped
    return render_template('profile.html', username=username)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = int(request.form['amount'])
        recipient = request.form['recipient']
        
        # No CSRF protection
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Get sender balance
        cursor.execute("SELECT balance FROM users WHERE id=?", (session['user_id'],))
        sender_balance = cursor.fetchone()[0]
        
        if sender_balance >= amount:
            # Update sender balance
            cursor.execute("UPDATE users SET balance = balance - ? WHERE id=?", 
                         (amount, session['user_id']))
            
            # Update recipient balance (SQLi vulnerable)
            cursor.execute(f"UPDATE users SET balance = balance + {amount} WHERE username='{recipient}'")
            conn.commit()
            message = f"Transferred ${amount} to {recipient}"
        else:
            message = "Insufficient funds"
        conn.close()
        return render_template('transfer.html', message=message)
    
    return render_template('transfer.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Unrestricted file upload
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            return f"File {filename} uploaded successfully!"
    
    return render_template('upload.html')

@app.route('/cookies')
def cookies():
    # Cookie manipulation test
    resp = make_response("Cookie set!")
    resp.set_cookie('test_cookie', 'cookie_value', httponly=False, secure=False)
    return resp

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)  # Debug mode enabled (security risk)