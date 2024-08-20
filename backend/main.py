import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from pathlib import Path
import sqlite3

# Configuration
app = Flask(__name__)
app.secret_key = '9dfeb43d7340b4b80817d514a1464c509060f354554fa2fc99922e608c7b7762'
JWT_SECRET_KEY = '6e9d4f12d4b6ea1b78672d76a987d0f2b5c1f91f90a1d3c36e6d6c8c1d0e5f2f'

JWT_EXPIRATION_DELTA = timedelta(days=1)

# Database helper functions
def create_db():
    '''Create a new database if the db doesn't exist'''
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE Task(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, task_date DATE, user_id INTEGER)")
    conn.commit()
    cur.execute("INSERT INTO Users VALUES (?,?,?)",[0,'admin','admin'])
    conn.commit()
    cur.close()
    conn.close()

def dict_factory(cursor, row):
    result = dict()
    for i, j in enumerate(cursor.description):
        result[j[0]] = row[i]
    return result

def open_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur = conn.cursor()
    return conn, cur

def close_db(conn, cur):
    cur.close()
    conn.close()

# JWT helper functions
def create_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(token):
    payload = decode_jwt_token(token)
    if payload:
        return payload['user_id']
    return None

# Initialize CORS and create the database if it doesn't exist
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
if not Path('./data.db').resolve().exists():
    create_db()

#------------------------------------login-------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    log = request.get_json()
    name = log.get("username")
    passwd = log.get("password")

    if '' in {name, passwd} or None in {name, passwd}:
        return jsonify({"error": "Bad Request: Invalid input"}), 400

    conn, cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE username = ?", [name]).fetchone()
    close_db(conn, cur)

    if user is None:
        return jsonify({"error": "User not found"}), 404
    if user['password'] == passwd:
        token = create_jwt_token(user["id"])
        return jsonify({"message": f"OK: Connected user {user['id']}", "token": token, "username": user["username"]}), 200
    return jsonify({"error": "Unauthorized: wrong password"}), 401

@app.route('/api/disconnection', methods=['POST'])
def disconnection():
    return jsonify({'message': 'Logged out'}), 200

#------------------------------------user-api-----------------------------------------------
@app.route('/api/users', methods=['POST'])
def add_user():
    '''Create users'''
    info = request.get_json()
    user = info.get('username')
    password = info.get('password')

    if '' in {user, password} or None in {user, password}:
        return jsonify({"error": "Bad Request: Invalid input"}), 400

    conn, cur = open_db()
    all_users = cur.execute("SELECT username FROM Users").fetchall()
    all_username = [dict.get(x, 'username') for x in all_users]

    if user in all_username:
        return jsonify({"error": "Conflict: User already exists"}), 409
    cur.execute("INSERT INTO Users (username, password) VALUES (?, ?)", [user, password])
    conn.commit()
    new_id = ((cur.execute("SELECT id FROM Users WHERE username = ?", [user]).fetchone()))['id']
    close_db(conn, cur)

    return jsonify({"id": new_id, "username": user}), 201

@app.route('/api/users', methods=['GET'])
def get_all_users():
    '''Get all users'''
    conn, cur = open_db()
    all_users = cur.execute("SELECT id, username FROM Users").fetchall()
    close_db(conn, cur)
    return jsonify(all_users), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    '''Get user by id'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    if user_id_from_token != user_id:
        return jsonify({"error": "Access Forbidden"}), 403

    conn, cur = open_db()
    user = cur.execute("SELECT id, username FROM Users WHERE id = ?", [user_id]).fetchone()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    close_db(conn, cur)
    return jsonify(user), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    '''Update user information'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    if user_id_from_token != user_id:
        return jsonify({"error": "Access Forbidden"}), 403

    new_info = request.get_json()
    user = new_info.get('username')
    password = new_info.get('password')
    new_password = new_info.get('new_password')

    if (user in {None, ''} and new_password in {None, ''}) or password in {None, ''}:
        return jsonify({"error": "Bad Request: Invalid input"}), 400

    conn, cur = open_db()
    user_data = cur.execute("SELECT password FROM Users WHERE id = ?", [user_id]).fetchone()

    if user_data is None:
        return jsonify({"error": "User not found"}), 404

    if password != user_data['password']:
        return jsonify({"error": "Unauthorized: wrong password"}), 401

    if user is not None:
        cur.execute("UPDATE Users SET username=? WHERE id=?", [user, user_id])
        conn.commit()
    if new_password is not None:
        cur.execute("UPDATE Users SET password=? WHERE id=?", [new_password, user_id])
        conn.commit()

    result = cur.execute("SELECT id, username FROM Users WHERE id=?", [user_id]).fetchone()
    close_db(conn, cur)
    return jsonify(result), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    '''Delete a user'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    if user_id_from_token != user_id:
        return jsonify({"error": "Access Forbidden"}), 403

    conn, cur = open_db()
    cur_del = cur.execute("SELECT * FROM Users WHERE id=?", [user_id]).fetchone()
    if cur_del is None:
        return jsonify({"error": "User not found"}), 404

    cur.execute("DELETE FROM Users WHERE id = ?", [user_id])
    cur.execute("DELETE FROM Task WHERE user_id = ?", [cur_del['id']])
    conn.commit()
    close_db(conn, cur)

    return jsonify(''), 204

#-----------------------------------task-api-----------------------------------------------
@app.route('/api/task/<int:user_id>', methods=['POST'])
def create_task(user_id):
    '''Create a new task'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    if user_id_from_token != user_id:
        return jsonify({"error": "Access Forbidden"}), 403

    task_info = request.get_json()
    task_desc = task_info.get("description")
    task_date = task_info.get("date")

    if '' in {task_desc, task_date} or None in {task_desc, task_date}:
        return jsonify({"error": "Bad Request: Invalid input"}), 400

    conn, cur = open_db()
    cur.execute("INSERT INTO Task (description, task_date, user_id) VALUES (?, ?, ?)", [task_desc, task_date, user_id])
    conn.commit()
    task_id = cur.execute("SELECT id FROM Task WHERE description=? AND user_id=?", [task_desc, user_id]).fetchone()['id']
    close_db(conn, cur)

    return jsonify({"id": task_id, "description": task_desc, "date": task_date}), 201

@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    '''Get a task by its id'''
    conn, cur = open_db()
    task = cur.execute("SELECT * FROM Task WHERE id = ?", [task_id]).fetchone()
    close_db(conn, cur)

    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200

@app.route('/api/task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    '''Update task information'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    task_info = request.get_json()
    description = task_info.get("description")
    date = task_info.get("date")

    if '' in {description, date} or None in {description, date}:
        return jsonify({"error": "Bad Request: Invalid input"}), 400

    conn, cur = open_db()
    task = cur.execute("SELECT * FROM Task WHERE id=?", [task_id]).fetchone()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if task['user_id'] != user_id_from_token:
        return jsonify({"error": "Access Forbidden"}), 403

    cur.execute("UPDATE Task SET description=?, task_date=? WHERE id=?", [description, date, task_id])
    conn.commit()
    close_db(conn, cur)

    return jsonify({"id": task_id, "description": description, "date": date}), 200

@app.route('/api/task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    '''Delete a task'''
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized: No token provided"}), 401

    user_id_from_token = get_current_user(token)
    if user_id_from_token is None:
        return jsonify({"error": "Unauthorized: Invalid token"}), 401

    conn, cur = open_db()
    task = cur.execute("SELECT * FROM Task WHERE id=?", [task_id]).fetchone()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if task['user_id'] != user_id_from_token:
        return jsonify({"error": "Access Forbidden"}), 403

    cur.execute("DELETE FROM Task WHERE id=?", [task_id])
    conn.commit()
    close_db(conn, cur)

    return jsonify(''), 204

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
