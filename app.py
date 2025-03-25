from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import time  # To simulate the heavy computation task

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT)''')

    # Create requests_log table to log every request
    cursor.execute('''CREATE TABLE IF NOT EXISTS requests_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT,
                        method TEXT,
                        timestamp TEXT)''')

    # Insert default users if the users table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        default_users = [
            ('Alice', 'alice@example.com'),
            ('Bob', 'bob@example.com'),
            ('Charlie2', 'charlie1@example.com'),
            ('Charlie1', 'charlie2@example.com'),
            ('Charlie3', 'charlie3@example.com'),
            ('Charlie5', 'charlie4@example.com'),
            ('Charlie6', 'charlie5@example.com')
        ]
        cursor.executemany('INSERT INTO users (name, email) VALUES (?, ?)', default_users)

    conn.commit()
    conn.close()

# Function to log each request
def log_request(endpoint, method):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('INSERT INTO requests_log (endpoint, method, timestamp) VALUES (?, ?, ?)',
                   (endpoint, method, timestamp))

    conn.commit()
    conn.close()

# Simulating heavy computation task (for example, a complex data processing task)
def simulate_heavy_computation():
    time.sleep(5)  # Simulating a heavy task that takes 5 seconds

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    log_request('/users', 'GET')  # Log the request

    # Simulate a heavy computation task only in this route
    simulate_heavy_computation()  # Simulate a heavy computation task

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    # Prepare response
    user_list = [{"id": user[0], "name": user[1], "email": user[2]} for user in users]

    conn.close()
    return jsonify(user_list)

# Route to get all logs without timestamp filter
@app.route('/all_logs', methods=['GET'])
def get_all_logs():
    log_request('/all_logs', 'GET')  # Log the request

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM requests_log')
    logs = cursor.fetchall()

    # Prepare logs for response
    log_list = [{"id": log[0], "endpoint": log[1], "method": log[2], "timestamp": log[3]} for log in logs]

    conn.close()

    return jsonify(log_list)

# Route to get logs based on a timestamp range (JSON body)
@app.route('/logs', methods=['POST'])
def get_logs():
    log_request('/logs', 'POST')  # Log the request

    # Get data from JSON body
    data = request.get_json()

    # Validate the data
    if not data or not data.get('start_time') or not data.get('end_time'):
        return jsonify({"error": "Please provide both 'start_time' and 'end_time' in the format YYYY-MM-DD HH:MM:SS"}), 400

    start_time = data['start_time']
    end_time = data['end_time']

    try:
        # Check if the times are in the correct format
        datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Time format must be YYYY-MM-DD HH:MM:SS"}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM requests_log
                      WHERE timestamp BETWEEN ? AND ?''', (start_time, end_time))
    logs = cursor.fetchall()

    # Prepare logs for response
    log_list = [{"id": log[0], "endpoint": log[1], "method": log[2], "timestamp": log[3]} for log in logs]

    conn.close()

    return jsonify(log_list)

# Route to count requests in a given time range (JSON body)
@app.route('/request_count', methods=['POST'])
def request_count():
    log_request('/request_count', 'POST')  # Log the request

    # Get data from JSON body
    data = request.get_json()

    # Validate the data
    if not data or not data.get('start_time') or not data.get('end_time'):
        return jsonify({"error": "Please provide both 'start_time' and 'end_time' in the format YYYY-MM-DD HH:MM:SS"}), 400

    start_time = data['start_time']
    end_time = data['end_time']

    try:
        # Check if the times are in the correct format
        datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Time format must be YYYY-MM-DD HH:MM:SS"}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT COUNT(*) FROM requests_log
                      WHERE timestamp BETWEEN ? AND ?''', (start_time, end_time))
    request_count = cursor.fetchone()[0]

    conn.close()

    return jsonify({"request_count": request_count})

if __name__ == '__main__':
    # Initialize the database and insert default users
    init_db()

    # Run the app
    app.run(debug=True)
