import sqlite3
from pathlib import Path 
from flask import Flask, jsonify, request, session
from datetime import datetime

# To change host and port, change the value of these variables 
host="127.0.0.1"
port=5000

def create_db():
    '''Create a new database if the db don't exists'''
    conn=sqlite3.connect("data.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE Task(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, task_date DATE, user_id INTEGER)")
    conn.commit()
    cur.execute("INSERT INTO Users VALUES (?,?,?)",[0,'admin','admin'])
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
    log = request.get_json()
    name = log.get("username")
    passwd = log.get("password")

    if '' in {name,passwd} or None in {name,passwd}:
        return jsonify({"error": "Bad Request: Invalid input"}),400

    if session.get('connected'):
        return jsonify({"error": "Forbidden: An user is already connected"}),403

    conn,cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE username = ?",[name]).fetchone()
    close_db(conn,cur)

    if user == None:
        return jsonify({"error" : "User not found"}),404
    if user['password'] == passwd:
        session['connected'] = True
        session['id'] = user["id"]
        return jsonify({"message":f"OK: Connected user {session['id']}","id": session['id'],"username": user["username"]}),200
    return jsonify({
        "error" : "Unauthorized: wrong password"}),401


@app.route('/api/disconnection',methods=['POST'])
def disconnection():
    if not session.get('connected'):
        return jsonify({"error": "Forbidden: No user connected"}),403
    session['connected'] = False
    session['id'] = None
    return jsonify(''),200

#------------------------------------user-api-----------------------------------------------
@app.route('/api/users',methods=['POST'])
def add_user():
    '''Create users'''
    if session.get('connected') and session.get("id") != 0 :
        return jsonify({"error": "Forbidden: Disconnect to create an account"}),403

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
    new_id = ((cur.execute("SELECT id FROM Users WHERE username = ?",[user]).fetchone()))['id']
    close_db(conn,cur)

    return jsonify({
        "id" : new_id,
        "username" : user
    }),201

@app.route('/api/users',methods=['GET'])
def get_all_users(): 
    '''Get all users'''
    if session.get('id') !=  0:
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    conn,cur = open_db()
    all_users = cur.execute("SELECT id,username FROM Users").fetchall()
    close_db(conn,cur)
    return jsonify(all_users),200

@app.route('/api/users/<int:user_id>',methods = ['GET'])
def get_user(user_id):
    '''Get user by id'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != 0 and session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403

    conn,cur = open_db()
    user = cur.execute("SELECT id,username FROM Users WHERE id = ?",[user_id]).fetchone()
    if user == None: return jsonify({"error": "User not found"}),404
    close_db(conn,cur)
    return jsonify(user),200

@app.route('/api/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    '''Update user information'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403

    new_info=request.get_json()
    user = new_info.get('username')
    password = new_info.get('password')
    new_password = new_info.get('new_password')

    if (user in {None,''} and new_password in {None,''}) or password in {None,''} :
        return jsonify({"error" : "Bad Request: Invalid input"}),400
    
    conn,cur = open_db()

    user_data = cur.execute("SELECT password FROM Users WHERE id = ?",[user_id]).fetchone()

    if user_data == None: 
        return jsonify({"error" : "User not found"}),404

    if password != user_data['password']:
        return jsonify({"error" : "Unauthorized: wrong password"}),401

    if user != None:
        cur.execute("UPDATE Users SET username=? WHERE id=?",[user,user_id])
        conn.commit()
    if new_password != None:
        cur.execute("UPDATE Users SET password=? WHERE id=?",[new_password,user_id])
        conn.commit()

    result = cur.execute("SELECT id,username FROM Users WHERE id=?",[user_id]).fetchone()
    close_db(conn,cur)
    return jsonify(result),200

@app.route('/api/users/<int:user_id>',methods=['DELETE'])
def delete_user(user_id):
    '''Delete an user'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != 0 and session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403
    conn,cur = open_db()
    cur_del=cur.execute("SELECT * FROM Users WHERE id=?",[user_id]).fetchone()
    if cur_del==None: return jsonify({"error": "User not found"}),404

    cur.execute("DELETE FROM Users WHERE id = ?",[user_id])
    cur.execute("DELETE FROM Task WHERE user_id = ?",[ cur_del['id'] ])
    conn.commit()
    close_db(conn,cur)

    session['connected'] = False
    session['id'] = None

    return jsonify(''),204

#-----------------------------------task-api-----------------------------------------------
@app.route('/api/task/<int:user_id>',methods=['POST'])
def create_task(user_id):
    '''Create a new task'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403

    task_info=request.get_json()
    task_desc = task_info.get("description")
    task_date = task_info.get("date")

    if '' in {task_desc,task_date} or None in {task_desc,task_date}:
        return jsonify({"error" : "Bad Request: Invalid input"}),400

    try:
        datetime.strptime(task_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Bad Request: Invalid date format"}), 400

    conn,cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchone()

    if user == None: 
        return jsonify({"error" : "User not found"}),404

    cur.execute("INSERT INTO Task(description,task_date,user_id) VALUES (?,?,?)",[task_desc,task_date,int(user_id)])
    conn.commit()

    task_id = (cur.execute("SELECT id FROM Task WHERE user_id = ? AND task_date = ? AND description = ?",[user_id,task_date,task_desc]).fetchone())['id']
    close_db(conn,cur)

    return jsonify({
        "id" : task_id,
        "description" : task_desc,
        "date" : task_date,
        "user_id" : user_id
    }),201


@app.route('/api/task/<int:user_id>/<int:task_id>',methods=['GET'])
def get_the_spec_task(user_id,task_id):
    '''Get the information about a specific task of an user'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403
    conn,cur = open_db()

    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchone()
    if user == None: return jsonify({"error": "User not found"}),404

    task = cur.execute("SELECT * FROM Task WHERE user_id = ? AND id =?",[user_id,task_id]).fetchone()
    if task == None: return jsonify({"error": "Task not found"}),404
    close_db(conn,cur)
    return jsonify(task),200

@app.route('/api/task/<int:user_id>',methods=['GET'])
def get_user_task(user_id):
    '''Get all task of an specific user'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403

    conn,cur = open_db()
    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchone()
    if user == None: return jsonify({"error": "User not found"}),404
    task = cur.execute("SELECT * FROM Task WHERE user_id = ? ",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(task),200

@app.route('/api/task/<int:user_id>/<int:task_id>', methods=['PUT'])
def update_a_task(user_id,task_id):
    '''Update the information about a specific task of an user'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403

    if request.method == 'PUT':
        task_info=request.get_json()
        task_desc = task_info.get("description")
        task_date = task_info.get("date")

        if task_date in {'',None} and task_desc in {'',None}:
            return jsonify({"error" : "Invalid input"}),400

        conn,cur = open_db()
        user = cur.execute("SELECT id FROM Users WHERE id = ?",[user_id]).fetchone()
        if user == None : return jsonify({"error": "User not found"}),404

        task = cur.execute("SELECT id FROM Task WHERE user_id = ? AND id = ?",[user_id,task_id]).fetchone()
        if task == None: return jsonify({"error": "Task not found"}),404

        if task_desc != None:
            cur.execute("UPDATE Task SET description = ? WHERE id=? AND user_id = ?",[task_desc,task_id,int(user_id)])
        
        if task_date != None:
            try:
                task_date = datetime.strptime(task_date, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Bad Request: Invalid date format"}), 400
            cur.execute("UPDATE Task SET task_date = ? WHERE id=? AND user_id = ?",[task_date,task_id,int(user_id)])
        
        conn.commit()

        cur_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchone()
        close_db(conn,cur)
        return jsonify(cur_task),200

@app.route('/api/task/<int:user_id>/<int:task_id>', methods=['DELETE'])
def delete_specific_task(user_id,task_id):
    '''Delete a specific task'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403
    conn,cur = open_db()

    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchone()
    if user == None: return jsonify({"error": "User not found"}),404

    del_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchone()
    if del_task == None: return jsonify({"error": "Task not found"}),404

    cur.execute("DELETE FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id])
    conn.commit()
    close_db(conn,cur)
    return jsonify(''),204


@app.route('/api/task/<int:user_id>',methods=['DELETE'])
def delete_all_task(user_id):
    '''Delete a specific task'''
    if not session.get("connected"):
        return jsonify({"error" : "Unauthorized: Action not allowed"}),401

    if session.get("id") != user_id:
        return jsonify({"error" : "Access Forbidden"}),403
    conn,cur = open_db()

    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchone()
    if user == None: return jsonify({"error": "User not found"}),404

    del_task = cur.execute("SELECT * FROM Task WHERE user_id = ?",[user_id]).fetchone()
    if del_task == None: return jsonify({"error": "Task not found"}),404

    cur.execute("DELETE FROM Task WHERE user_id = ?",[user_id])
    conn.commit()
    close_db(conn,cur)
    return jsonify(''),204

    
if __name__ == "__main__":
    app.debug=True
    app.run(host=host,port=port)


