from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json
import re
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
HISTORY_PATH = 'planner_history.json'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'raas@2006'
app.config['MYSQL_DB'] = 'Daily_Planner'

# Initialize MySQL
mysql = MySQL(app)

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history, f)

def generate_planner(tasks, task_times, start_time):
    planner = []
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        try:
            start_time_obj = datetime.strptime(start_time, "%I %p")
        except ValueError:
            return ["Invalid time format. Please use 'HH:MM' for 24-hour format or 'HH AM/PM' for 12-hour format."]

    for task in tasks:
        task = task.strip()
        try:
            task_duration = float(task_times[task])
            end_time_obj = start_time_obj + timedelta(hours=task_duration)
            planner.append(f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}: {task}")
            start_time_obj = end_time_obj
        except ValueError:
            return [f"Invalid duration format for task '{task}'. Please enter the duration in hours (e.g., '1.5')."]

    return planner

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home_1')
def home_1():
    return render_template('home_1.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/notes')
def notes():
    return render_template('notes.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['username'] = account['username']
            session['password'] = account['password']
            return redirect(url_for('home_1'))
        else:
            return 'Incorrect username/password!'
    
    return render_template('login.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']
        confirm_password = request.form['psw-repeat']

        if password == confirm_password:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query = "INSERT INTO accounts (username, password) VALUES (%s, %s)"
                values = (username, password)
                cursor.execute(query, values)
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('home'))
            except Exception as e:
                print('Error:', e)
                mysql.connection.rollback()
                return jsonify({'error': 'Database error'})
        else:
            return jsonify({'error': 'Passwords do not match'})
    return render_template('reg.html')

@app.route('/calender')
def calender():
    return render_template('Calender.html')

@app.route('/planner', methods=['POST'])
def planner():
    tasks_input = request.form['tasks_input']
    tasks = re.split(r',\s*|\s+and\s+', tasks_input)
    important_task = request.form['important_task']

    task_times = {task.strip(): request.form.get(f'task_{task.strip()}_time') for task in tasks}
    start_time = request.form['start_time']

    planner_messages = []
    planner = generate_planner(tasks, task_times, start_time)

    if isinstance(planner, list) and isinstance(planner[0], str) and "Invalid" in planner[0]:
        planner_messages = planner
        planner = []

    if not planner_messages:
        history = load_history()
        new_entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tasks_input': tasks_input,
            'important_task': important_task,
            'start_time': start_time,
            'task_times': task_times,
            'planner': planner
        }
        history.append(new_entry)
        history = history[-7:]
        save_history(history)

    return render_template('planner.html', planner=planner, planner_messages=planner_messages)

@app.route('/update_planner', methods=['POST'])
def update_planner():
    updated_planner = [request.form.get(key) for key in request.form if key.startswith('planner_item_')]
    history = load_history()
    if history:
        history[-1]['planner'] = updated_planner
        save_history(history)
    return render_template('planner.html', planner=updated_planner)

@app.route('/history')
def view_history():
    history = load_history()
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)
