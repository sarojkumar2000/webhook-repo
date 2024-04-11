from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']
collection = db['events']

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {'_id': 0}))
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('event_type')
    payload = data.get('payload')

    if event_type in ['push', 'pull_request', 'merge']:
        handle_event(event_type, payload)
    return '', 200

def handle_event(event_type, payload):
    if event_type == 'push':
        handle_push_event(payload)
    elif event_type == 'pull_request':
        handle_pull_request_event(payload)
    elif event_type == 'merge':
        handle_merge_event(payload)

def handle_push_event(payload):
    author = payload['sender']['login']
    to_branch = payload['ref'].split('/')[-1]
    timestamp = payload['repository']['pushed_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'action': 'push',
        'author': author,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def handle_pull_request_event(payload):
    author = payload['sender']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = payload['pull_request']['created_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'action': 'pull_request',
        'author': author,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def handle_merge_event(payload):
    author = payload['sender']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = payload['pull_request']['merged_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'action': 'merge',
        'author': author,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def format_timestamp(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    return dt.strftime('%d %B %Y - %I:%M %p UTC')

if __name__ == '__main__':
    app.run(debug=True)
