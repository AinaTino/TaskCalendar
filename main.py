import sqlite3
from pathlib import Path 
import requests
from flask import Flask, jsonify, request, session

# To change host and port, change the value of these variables 
host="127.0.0.1"
port=5000

def create_db():
    '''Create a new database if the db don't exists'''
    conn=sqlite3.connect("data.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE Users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE Task(id INTEGER PRIMARY KEY, description TEXT, task_date DATE, user_id INTEGER)")
    conn.commit()
    cur.close()
    conn.close()

def dict_factory(cursor,row):
    result=dict()
    for i,j in enumerate(cursor.description):
        result[j[0]] = row[i]
    return result

def open_db():
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    return conn,cur

def close_db(conn,cur):
    cur.close()
    conn.close()

app=Flask(__name__)

app.secret_key = '9dfeb43d7340b4b80817d514a1464c509060f354554fa2fc99922e608c7b7762'

if not Path('./data.db').resolve().exists() :
    create_db()

#------------------------------------login-------------------------------------------------
@app.route('/api/login',methods =['POST'])
def login():
    all_user = (requests.get(f"http://{host}:{port}/api/users")).json()
    log = request.get_json()
    name = log.get("username")
    passwd = log.get("password")

    if '' in {name,passwd} or None in {name,passwd}:
        return jsonify({"error": "Bad Request: Invalid input"}),400

    if session.get('connected'):
        return jsonify({"error": "Forbidden: An user is already connected"}),403

    for i in all_user:
        if i["username"] == name:
            if i["password"] == passwd:
                return jsonify({"message":"OK: Connected"}),200
                session['connected'] = True
            return jsonify({"error" : "Unauthorized: wrong password"}),401
    return jsonify({"error" : "User not found"}),404


@app.route('/api/disconnection',methods=['POST'])
def disconnection():
    if not session.get('connected'):
        return jsonify({"error": "Forbidden: No user connected"}),403
    session['connected'] = False
    return jsonify(''),200

#------------------------------------user-api-----------------------------------------------
@app.route('/api/users',methods=['POST'])
def add_user():
    '''Create users'''
    info=request.get_json()
    user= info.get('username')
    password = info.get('password')

    if '' in {user,password} or None in {user,password}:
        return jsonify({"error" : "Bad Request: Invalid input"}),400

    conn,cur = open_db()
    all_users = cur.execute("SELECT username FROM Users").fetchall() 
    all_username = [dict.get(x,'username') for x in all_users]

    if user in all_username:
        return jsonify({"error": "Conflict: User already exists"}),409
    cur.execute("INSERT INTO Users (username,password) VALUES (?,?)",[user,password])
    conn.commit()
    new_id = ((cur.execute("SELECT id FROM Users WHERE username = ?",[user]).fetchall())[0])['id']
    close_db(conn,cur)

    return jsonify({
        "id" : new_id,
        "username" : user,
        "password" : password
    }),201

@app.route('/api/users',methods=['GET'])
def get_all_users(): 
    '''Get all users'''
    conn,cur = open_db()
    all_users = cur.execute("SELECT * FROM Users").fetchall()
    close_db(conn,cur)
    return jsonify(all_users),200

@app.route('/api/users/<int:user_id>',methods = ['GET'])
def get_user(user_id):
    '''Get user by id'''
    conn,cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()
    if len(user)==0: return jsonify({"error": "User not found"}),404
    close_db(conn,cur)
    return jsonify(user[0]),200

@app.route('/api/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    '''Update user information'''
    new_info=request.get_json()
    user = new_info.get('username')
    password = new_info.get('password')

    if user in {None,''} and password in {None,''}:
        return jsonify({"error" : "Bad Request: Invalid input"}),400
    
    conn,cur = open_db()

    user_data = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()
    if len(user_data) == 0: 
        return jsonify({"error" : "User not found"}),404

    if user != None:
        cur.execute("UPDATE Users SET username=? WHERE id=?",[user,user_id])
        conn.commit()
    if password != None:
        cur.execute("UPDATE Users SET password=? WHERE id=?",[password,user_id])
        conn.commit()
    result = cur.execute("SELECT * FROM Users WHERE id=?",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(result[0]),200

@app.route('/api/users/<int:user_id>',methods=['DELETE'])
def delete_user(user_id):
    '''Delete an user'''
    conn,cur = open_db()
    cur_del=cur.execute("SELECT * FROM Users WHERE id=?",[user_id]).fetchall()
    if len(cur_del)==0: return jsonify({"error": "User not found"}),404

    cur.execute("DELETE FROM Users WHERE id = ?",[user_id])
    cur.execute("DELETE FROM Task WHERE user_id = ?",[ (cur_del[0])['id'] ])
    conn.commit()
    close_db(conn,cur)
    return jsonify(''),204

#-----------------------------------task-api-----------------------------------------------
@app.route('/api/task/<int:user_id>',methods=['POST'])
def create_task(user_id):
    '''Create a new task'''
    task_info=request.get_json()
    task_desc = task_info.get("description")
    task_date = task_info.get("date")

    if '' in {task_desc,task_date} or None in {task_desc,task_date}:
        return jsonify({"error" : "Bad Request: Invalid input"}),400

    conn,cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()

    if len(user) == 0: 
        return jsonify({"error" : "User not found"}),404

    cur.execute("INSERT INTO Task(description,task_date,user_id) VALUES (?,?,?)",[task_desc,task_date,user_id])
    conn.commit()

    task_id = ((cur.execute("SELECT id FROM Task WHERE user_id = ? AND task_date = ? AND description = ?",[user_id,task_date,task_desc]).fetchall())[0])['id']
    close_db(conn,cur)

    return jsonify({
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
    }),201


@app.route('/api/task/<int:user_id>/<int:task_id>',methods=['GET'])
def get_task(user_id,task_id):
    '''Get the information about a specific task of an user'''
    conn,cur = open_db()

    all_user = cur.execute("SELECT * FROM Users WHERE id = ?",user_id).fetchall()
    if len(all_user) == 0: return jsonify({"error": "User not found"}),404

    task = cur.execute("SELECT * FROM Task WHERE user_id = ? AND id =?",[user_id,task_id]).fetchall()
    if len(task) == 0: return jsonify({"error": "Task not found"}),404
    close_db(conn,cur)
    return jsonify(task[0]),200


@app.route('/api/task',methods=['GET'])
def get_all_task():
    '''Get all task of any user'''
    conn,cur = open_db()
    task = cur.execute("SELECT * FROM Task ").fetchall()
    close_db(conn,cur)
    return jsonify(task),200


@app.route('/api/task/<int:user_id>',methods=['GET'])
def get_user_task(user_id):
    '''Get all task of an specific user'''
    conn,cur = open_db()
    all_user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()
    if len(all_user) == 0: return jsonify({"error": "User not found"}),404
    task = cur.execute("SELECT * FROM Task WHERE user_id = ? ",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(task),200


@app.route('/api/task/<int:user_id>',methods=['DELETE'])
def delete_task(user_id):
    '''Delete a specific task'''
    conn,cur = open_db()

    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()
    if len(user) == 0: return jsonify({"error": "User not found"}),404

    del_task = cur.execute("SELECT * FROM Task WHERE user_id = ?",[user_id]).fetchall()
    if len(del_task) == 0: return jsonify({"error": "Task not found"}),404

    cur.execute("DELETE FROM Task WHERE user_id = ?",[user_id])
    conn.commit()
    close_db(conn,cur)
    return jsonify(''),204


@app.route('/api/task/<int:user_id>/<int:task_id>', methods=['PUT','DELETE'])
def update_task(user_id,task_id):
    '''Update the information about a specific task of an user'''
    if requests.methods == 'PUT':
        task_info=request.get_json()
        task_desc = task_info.get("description")
        task_date = task_info.get("date")

        if task_date in {'',None} or task_desc in {'',None}:
            return jsonify({"error" : "Invalid input"}),400

        conn,cur = open_db()
        user = cur.execute("SELECT id FROM Users WHERE id = ?",[user_id]).fetchall()
        if len(user): return jsonify({"error": "User not found"}),404

        task = cur.execute("SELECT id FROM Task WHERE user_id = ? AND id = ?",[user_id,task_id]).fetchall()
        if len(task): return jsonify({"error": "Task not found"}),404

        if task_desc != None:
            cur.execute("UPDATE Task SET description = ? WHERE id=? AND user_id = ?",[task_desc,task_id,user_id])
        if task_date != None:
            cur.execute("UPDATE Task SET task_date = ? WHERE id=? AND user_id = ?",[task_date,task_id,user_id])
        conn.commit()

        cur_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchall()
        close_db(conn,cur)
        return jsonify(cur_task[0]),200

# @app.route('/api/task/<int:user_id>/<int:task_id>', methods=['DELETE'])
# def delete_task(user_id,task_id):
#     '''Delete a specific task'''
    elif requests.methods == 'DELETE' : # Manao AssertionError:View function mapping is overwriting an existing endpoint function: delete_task
        #Foana leizy de nataoko an'izao
        conn,cur = open_db()

        user = cur.execute("SELECT * FROM Users WHERE id = ?",user_id).fetchall()
        if len(user)==0: return jsonify({"error": "User not found"}),404

        del_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchall()
        if len(del_task) == 0: return jsonify({"error": "Task not found"}),404

        cur.execute("DELETE FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id])
        conn.commit()
        close_db(conn,cur)
        return jsonify(''),204

    
if __name__ == "__main__":
    app.debug=True
    app.run(host=host,port=port)


