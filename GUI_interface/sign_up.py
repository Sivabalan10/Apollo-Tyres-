from flask import Flask, render_template, request, redirect, Response, jsonify, send_file, url_for
import sqlite3
import threading
app = Flask(__name__)

def create_new_user(username, password):
    # Create a lock
    db_lock = threading.Lock()
    # Acquire the lock before accessing the database
    with db_lock:
        # Connect to the database
        conn = sqlite3.connect('config.db')
        cursor = conn.cursor()

        # Execute SQL queries
        cursor.execute('SELECT * FROM users')

        # Release the lock after accessing the database
        conn.close()

    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert new user into the users table
    cursor.execute('''INSERT INTO users (username, password)
                      VALUES (?, ?)''', (username, password))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"New user '{username}' created successfully.")


@app.route('/')
def homepage():
    return render_template("sign_up.html")


@app.route('/signup', methods=['POST'])
def signup():
    username_2 = request.form.get('username')
    password_2 = request.form.get('password')
    create_new_user(username_2, password_2)
    return "<h3>Account added successfully</h3>"


if __name__ == "__main__":
    app.run(debug=True)