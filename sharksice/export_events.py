"""Export events from SQLite database to JSON."""
import sqlite3
import json
import pathlib
from datetime import datetime

DB_PATH = pathlib.Path(__file__).parent.parent / "events.db"
OUTPUT_PATH = pathlib.Path(__file__).parent.parent / "data" / "events.json"


def export_events_to_json():
    """Export all events from the database to a JSON file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM events ORDER BY start_date')
    rows = cursor.fetchall()
    
    events = []
    for row in rows:
        event = dict(row)
        # Convert timestamps to ISO format strings for JSON serialization
        for date_field in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if event.get(date_field):
                try:
                    # Parse the timestamp and convert to ISO format
                    dt = datetime.fromisoformat(event[date_field])
                    event[date_field] = dt.isoformat()
                except (ValueError, TypeError):
                    pass
        events.append(event)
    
    conn.close()
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"Exported {len(events)} events to {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    export_events_to_json()
