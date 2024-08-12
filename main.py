import sqlite3
from pathlib import Path 
import requests
from flask import Flask, jsonify, request, session

host="127.0.0.1"
port=6969

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

def close_db(conn,cur):
    cur.close()
    conn.close()

app=Flask(__name__)

app.secret_key = '9dfeb43d7340b4b80817d514a1464c509060f354554fa2fc99922e608c7b7762'

if not Path('./data.db').resolve().exists() :
    create_db()

#------------------------------------login-------------------------------------------------
@app.route('/api/login',methods =['GET'])
def login():
    all_user = (requests.get(f"http://{host}:{port}/api/users")).json()
    log = request.get_json()
    name = log.get("username")
    passwd = log.get("password")
    if session.get('connected'):
        return jsonify("Error: An user is already connected")
    for i in all_user:
        if i["username"] == name:
            if i["password"] == passwd:
                return jsonify("Success")
                session['connected'] = True
            return jsonify("Error: Wrong password")
    return "Error: User not found"

@app.route('/api/disconnection',methods=['GET'])
def disconnection():
    session['connected'] = False
    return jsonify("Deconnected")

#------------------------------------user-api-----------------------------------------------
@app.route('/api/users',methods=['POST'])
def add_user():
    '''Create users'''
    info=request.get_json()
    user= info.get('username')
    password = info.get('password')
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    all_users = cur.execute("SELECT * FROM Users").fetchall() 
    all_username = [dict.get(x,'username') for x in all_users]
    if user in all_username:
        return jsonify('Error: User already exists')
    new_id = len(all_username) + 1
    cur.execute("INSERT INTO Users VALUES (?,?,?)",[new_id,user,password])
    all_users.append({
        "id" : new_id,
        "username" : user,
        "pwd" : password,
    })
    conn.commit()
    close_db(conn,cur)
    print(cur.execute("SELECT * FROM Users ").fetchall())
    return jsonify(all_users)

@app.route('/api/users',methods=['GET'])
def get_all_users(): 
    '''Get all users'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    all_users = cur.execute("SELECT * FROM Users").fetchall()
    close_db(conn,cur)
    return jsonify(all_users)

@app.route('/api/users/<int:user_id>',methods = ['GET'])
def get_user(user_id):
    '''Get user by id'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    user = cur.execute("SELECT * FROM Users WHERE id = ?",[user_id]).fetchall()
    if len(user)==0: return jsonify("Error: User not found")
    close_db(conn,cur)
    return jsonify(user[0])

@app.route('/api/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    '''Update user information'''
    new_info=request.get_json()
    user = new_info.get('username')
    password = new_info.get('password')
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    if user != None:
        cur.execute("UPDATE Users SET username=? WHERE id=?",[user,user_id])
        conn.commit()
    if password != None:
        cur.execute("UPDATE Users SET password=? WHERE id=?",[password,user_id])
        conn.commit()
    result = cur.execute("SELECT * FROM Users WHERE id=?",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(result[0])

@app.route('/api/users/<int:user_id>',methods=['DELETE'])
def delete_user(user_id):
    '''Delete an user'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    cur_del=cur.execute("SELECT * FROM Users WHERE id=?",[user_id]).fetchall()
    if len(cur_del)==0: return jsonify("Error: User not found")
    cur.execute("DELETE FROM Users WHERE id = ?",[user_id])
    cur.execute("DELETE FROM Task WHERE user_id = ?",[ (cur_del[0])['id'] ])
    conn.commit()
    close_db(conn,cur)
    return jsonify(cur_del[0])

#-----------------------------------task-api-----------------------------------------------
@app.route('/api/task/<int:user_id>',methods=['POST'])
def create_task(user_id):
    '''Create a new task'''
    task_info=request.get_json()
    task_desc = task_info.get("description")
    task_date = task_info.get("date")
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    all_users = cur.execute("SELECT id FROM Users").fetchall()
    if user_id not in [x['id'] for x in all_users]: return jsonify("Error: User not found")
    task_id = len(cur.execute("SELECT * FROM Task").fetchall()) + 1
    cur.execute("INSERT INTO Task VALUES (?,?,?,?)",[task_id,task_desc,task_date,user_id])
    conn.commit()
    all_task = cur.execute("SELECT * FROM Task WHERE user_id = ?",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(all_task)

@app.route('/api/task/<int:user_id>/<int:task_id>',methods=['GET'])
def get_task(user_id,task_id):
    '''Get the information about a specific task of an user'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    task = cur.execute("SELECT * FROM Task WHERE user_id = ? AND id =?",[user_id,task_id]).fetchall()
    if len(task) == 0: return jsonify("Error: Task not found")
    close_db(conn,cur)
    return jsonify(task[0])

@app.route('/api/task/<int:user_id>',methods=['GET'])
def get_user_task(user_id):
    '''Get all task of an specific user'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    task = cur.execute("SELECT * FROM Task WHERE user_id = ? ",[user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(task)

@app.route('/api/task/<int:user_id>',methods=['DELETE'])
def delete_task(user_id):
    '''Delete a specific task'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()

    all_users = cur.execute("SELECT id FROM Users").fetchall()
    if user_id not in [x['id'] for x in all_users]: return jsonify("Error: User not found")

    del_task = cur.execute("SELECT * FROM Task WHERE user_id = ?",[user_id]).fetchall()
    if len(del_task) == 0: return jsonify("Error: Task not found")
    cur.execute("DELETE FROM Task WHERE user_id = ?",[user_id])
    conn.commit()
    close_db(conn,cur)
    return jsonify(del_task)

@app.route('/api/task',methods=['GET'])
def get_all_task():
    '''Get all task of any user'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    task = cur.execute("SELECT * FROM Task ").fetchall()
    close_db(conn,cur)
    return jsonify(task)

@app.route('/api/task/<int:user_id>/<int:task_id>', methods=['PUT'])
def update_task(user_id,task_id):
    '''Update the information about a specific task of an user'''
    task_info=request.get_json()
    task_desc = task_info.get("description")
    task_date = task_info.get("date")
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()
    all_users = cur.execute("SELECT id FROM Users").fetchall()
    if user_id not in [x['id'] for x in all_users]: return jsonify("Error: User not found")
    all_task = cur.execute("SELECT id FROM Task WHERE user_id = ?",[user_id]).fetchall()
    if task_id not in [x['id'] for x in all_task]: return jsonify("Error: Task not found")
    
    if task_desc != None:
        cur.execute("UPDATE Task SET description = ? WHERE id=? AND user_id = ?",[task_desc,task_id,user_id])
    if task_date != None:
        cur.execute("UPDATE Task SET task_date = ? WHERE id=? AND user_id = ?",[task_date,task_id,user_id])
    conn.commit()
    cur_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchall()
    close_db(conn,cur)
    return jsonify(cur_task[0])

@app.route('/api/task/<int:user_id>/<int:task_id>', methods=['DELETE'])
def delete_task(user_id,task_id):
    '''Delete a specific task'''
    conn=sqlite3.connect("data.db")
    conn.row_factory = dict_factory
    cur=conn.cursor()

    all_users = cur.execute("SELECT id FROM Users").fetchall()
    if user_id not in [x['id'] for x in all_users]: return jsonify("Error: User not found")
    all_task = cur.execute("SELECT id FROM Task WHERE user_id = ?",[user_id]).fetchall()
    if task_id not in [x['id'] for x in all_task]: return jsonify("Error: Task not found")

    del_task = cur.execute("SELECT * FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id]).fetchall()
    if len(del_task) == 0: return jsonify("Error: Task not found")
    cur.execute("DELETE FROM Task WHERE id = ? AND user_id = ?",[task_id,user_id])
    conn.commit()
    close_db(conn,cur)
    return jsonify(del_task[0])

    
if __name__ == "__main__":
    app.debug=True
    app.run(host=host,port=port)


    