import sys
import os
import requests
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json

checkson_dir = os.environ['CHECKSON_DIR']

def write_message(message):
    print(message)
    with open(f"{checkson_dir}/message", "w") as f:
        f.write(message)

url = "https://api.gcmb.io/api/orgs/adsb/projects/adsb/publish-stats"

r = requests.get(url)
r.raise_for_status()

stats = r.json()

# Parse as ISO 8601 date
last_timestamp = datetime.fromisoformat(stats['lastTimestamp'])

# Check if the last timestamp is within the last 5 minutes
if last_timestamp.astimezone(timezone.utc) < datetime.now().astimezone(timezone.utc) - timedelta(minutes=5):
    write_message(f"Last timestamp is {last_timestamp}, which is more than 5 minutes ago")
    sys.exit(1)

number_of_messages = int(stats['prevMinuteCount'])

if number_of_messages < 100:
    write_message(f"Number of messages in last minute is {number_of_messages}, which is less than 100")
    sys.exit(1)

write_message(f"Check successful. Stats: {json.dumps(stats)}")
