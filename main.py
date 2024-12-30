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


def check_stat_timestamp(stats, max_minutes):
    last_timestamp = datetime.fromisoformat(stats['lastTimestamp'])
    # Check if the last timestamp is within the last max_minutes minutes
    return last_timestamp.astimezone(timezone.utc) > datetime.now().astimezone(timezone.utc) - timedelta(minutes=max_minutes)


def check_adsb():
    url = "https://api.gcmb.io/api/orgs/adsb/projects/adsb/publish-stats"

    r = requests.get(url)
    r.raise_for_status()

    stats = r.json()

    if not check_stat_timestamp(stats, 5):
        write_message(f"Last timestamp is {stats['lastTimestamp']}, which is more than 5 minutes ago")
        sys.exit(1)

    number_of_messages = int(stats['prevMinuteCount'])

    if number_of_messages < 100:
        write_message(f"Number of messages in last minute is {number_of_messages}, which is less than 100")
        sys.exit(1)

    print(f"ADS-B check successful, stats: {stats}")


def check_smard():
    url = "https://api.gcmb.io/api/orgs/stefan/projects/smard/publish-stats"

    r = requests.get(url)
    r.raise_for_status()

    stats = r.json()

    if not check_stat_timestamp(stats, 30):
        write_message(f"Last timestamp is {stats['lastTimestamp']}, which is more than 30 minutes ago")
        sys.exit(1)

    number_of_messages = int(stats['prevHourCount'])

    if number_of_messages < 100:
        write_message(f"Number of messages in previous hour is {number_of_messages}, which is less than 100")
        sys.exit(1)

    print(f"SMARD check successful, stats: {stats}")


def main():
    check_adsb()
    check_smard()
    write_message(f"All checks successful")


if __name__ == "__main__":
    main()
