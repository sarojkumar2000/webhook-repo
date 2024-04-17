from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client.get_database('github_events')
collection = db.get_collection('events') 

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {'_id': 0}))
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('event_type')
    payload = data.get('payload')
    request_id = get_request_id(event_type, payload)

    if event_type in ['push', 'pull_request', 'merge']:
        handle_event(event_type, payload, request_id)
    return '', 200

def handle_event(event_type, payload, request_id):
    if event_type == 'push':
        handle_push_event(payload, request_id)
    elif event_type == 'pull_request':
        handle_pull_request_event(payload, request_id)
    elif event_type == 'merge':
        handle_merge_event(payload, request_id)

def handle_push_event(payload, request_id):
    author = payload['sender']['login']
    to_branch = payload['ref'].split('/')[-1]
    timestamp = payload['repository']['pushed_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'request_id': request_id,
        'action': 'push',
        'author': author,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def handle_pull_request_event(payload, request_id):
    author = payload['sender']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = payload['pull_request']['created_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'request_id': request_id,
        'action': 'pull_request',
        'author': author,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def handle_merge_event(payload, request_id):
    author = payload['sender']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = payload['pull_request']['merged_at']
    formatted_timestamp = format_timestamp(timestamp)
    collection.insert_one({
        'request_id': request_id,
        'action': 'merge',
        'author': author,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': formatted_timestamp
    })

def format_timestamp(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    day = dt.strftime('%d')
    formatted_day = add_ordinal_suffix(int(day))
    formatted_time = dt.strftime('{} %B %Y - %I:%M%p UTC').format(formatted_day)
    return formatted_time

def add_ordinal_suffix(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return str(day) + suffix


def get_request_id(event_type, payload):
    if event_type == 'push':
        return payload.get('after')
    elif event_type == 'pull_request':
        return payload.get('pull_request', {}).get('id')
    elif event_type == 'merge':
        return payload.get('pull_request', {}).get('id')


if __name__ == '__main__':
    app.run(debug=True)
