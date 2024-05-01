from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb://127.0.0.1:27017/')


db = client["EventsDB1"]


collection = db["Events"]


def get_ordinal_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return suffix


def format_timestamp(timestamp):
    ordinal_day = get_ordinal_suffix(timestamp.day)
    formatted_timestamp = timestamp.strftime(f"%d{ordinal_day} %B %Y - %I:%M%p UTC")
    return formatted_timestamp


@app.route('/github_events', methods=['POST'])
def github_events():
    event_data = request.get_json()
    if event_data:
        sender = event_data.get('sender', {}).get('login')
        ref = event_data.get('ref')
        base_ref = event_data.get('base_ref')
        head_commit = event_data.get('head_commit')
        pull_request = event_data.get('pull_request')

        timestamp = datetime.utcnow()
        formatted_timestamp = format_timestamp(timestamp)

        if head_commit and 'distinct' in head_commit:
            event_type = "PUSH"
            request_id = head_commit.get('id')
            to_branch = ref.split("/")[-1] if ref else "Unknown"
            event_desc = f'"{sender}" pushed to "{to_branch}"'
        elif base_ref and 'pull_request' in base_ref:
            event_type = "PULL_REQUEST"
            request_id = pull_request.get('id')
            print(event_type)

  
            from_branch = event_data.get('base', {}).get('ref') if 'base' in event_data else "Unknown"
            to_branch = event_data.get('head', {}).get('ref') if 'head' in event_data else "Unknown"
            pull_request_title = pull_request.get('title') if 'title' in pull_request else " (title missing)"

            event_desc = f'"{sender}" submitted a pull request: "{pull_request_title}" from "{from_branch}" to "{to_branch}"'
        elif event_data.get('action') == 'closed' and pull_request:
            event_type = "MERGE"
            request_id = pull_request.get('number')
            from_branch = base_ref.split("/")[-1] if base_ref else "Unknown"
            to_branch = event_data.get('merged_branch')  
            event_desc = f'"{sender}" merged branch "{from_branch}" to "{to_branch}"'
        else:
            return jsonify({"error": "Invalid event"}), 400

        # Storing event data into DB
        event_doc = {
            "event_type": event_type,
            "request_id": request_id,
            "event_description": event_desc,
            "timestamp": formatted_timestamp,
        }
        collection.insert_one(event_doc)

        return jsonify({"message": "Event stored successfully"}), 200
    else:
        return jsonify({"error": "Invalid request data"}), 400


if __name__ == '__main__':
    app.run(debug=True)