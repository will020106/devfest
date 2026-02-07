from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(_name_, static_folder='.')
CORS(app)  # Allow frontend to talk to backend

# Simple file-based "database"
DATA_FILE = 'data.json'

def load_data():
    """Load all data from JSON file"""
    if not os.path.exists(DATA_FILE):
        # Default data structure
        default_data = {
            'users': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'role': 'admin'},
                {'id': 2, 'name': 'Alice Smith', 'email': 'alice@example.com', 'role': 'member'}
            ],
            'channels': [
                {'id': 1, 'name': 'general', 'description': 'General discussion', 'created_by': 1},
                {'id': 2, 'name': 'random', 'description': 'Random chat', 'created_by': 1}
            ],
            'messages': [
                {'id': 1, 'channel_id': 1, 'user_id': 1, 'text': 'Welcome to FlowHQ!', 'timestamp': '2024-01-15 10:00:00'},
                {'id': 2, 'channel_id': 1, 'user_id': 2, 'text': 'Thanks, excited to be here!', 'timestamp': '2024-01-15 10:05:00'}
            ],
            'events': [
                {'id': 1, 'title': 'Team Standup', 'start': '2024-01-16T09:00:00', 'end': '2024-01-16T09:30:00', 'organizer': 1}
            ],
            'tasks': []
        }
        save_data(default_data)
        return default_data
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Save all data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# API: Get all data (for initial load)
@app.route('/api/data')
def get_all_data():
    return jsonify(load_data())

# API: Add a message
@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    db = load_data()
    
    new_message = {
        'id': len(db['messages']) + 1,
        'channel_id': data['channel_id'],
        'user_id': data.get('user_id', 1),  # Default to user 1
        'text': data['text'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    db['messages'].append(new_message)
    save_data(db)
    
    return jsonify(new_message)

# API: Add a calendar event
@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    db = load_data()
    
    new_event = {
        'id': len(db['events']) + 1,
        'title': data['title'],
        'start': data['start'],
        'end': data['end'],
        'description': data.get('description', ''),
        'organizer': data.get('organizer', 1),
        'attendees': data.get('attendees', [1, 2])
    }
    
    db['events'].append(new_event)
    save_data(db)
    
    return jsonify(new_event)

# API: Add a task
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    db = load_data()
    
    new_task = {
        'id': len(db['tasks']) + 1,
        'text': data['text'],
        'assigned_to': data.get('assigned_to'),
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    
    db['tasks'].append(new_task)
    save_data(db)
    
    return jsonify(new_task)

# API: Update task completion
@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    db = load_data()
    
    for task in db['tasks']:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            save_data(db)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

# API: Mock AI response
@app.route('/api/ai/ask', methods=['POST'])
def ask_ai():
    question = request.json.get('question', '').lower()
    
    responses = {
        'meeting': "You have 2 meetings today: Team Standup at 9 AM and Q2 Planning at 2 PM.",
        'task': "You have 3 pending tasks: 1) Prepare slides 2) Review budget 3) Update timeline",
        'schedule': "Click the 'Schedule Meeting' button to add a new event to the calendar.",
        'default': "I can help with meetings, tasks, and team updates. Try asking about your schedule."
    }
    
    if 'meeting' in question:
        response = responses['meeting']
    elif 'task' in question:
        response = responses['task']
    elif 'schedule' in question:
        response = responses['schedule']
    else:
        response = responses['default']
    
    return jsonify({'response': response})

if _name_ == '_main_':
    app.run(debug=True, port=5000)