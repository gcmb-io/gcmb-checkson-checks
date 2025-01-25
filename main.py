import sys
import os
import requests
from datetime import datetime
from datetime import timedelta
from datetime import timezone

checkson_dir = os.environ['CHECKSON_DIR']

def write_message(message):
    print(message)
    with open(f"{checkson_dir}/message", "w") as f:
        f.write(message)


def check_stat_timestamp(stats, max_minutes):
    last_timestamp = datetime.fromisoformat(stats['lastTimestamp'])
    # Check if the last timestamp is within the last max_minutes minutes
    return last_timestamp.astimezone(timezone.utc) > datetime.now().astimezone(timezone.utc) - timedelta(minutes=max_minutes)


def check(org, project, last_timestamp_in_minutes=None, min_messages_prev_hour=None, min_messages_prev_minute=None):
    url = f"https://api.gcmb.io/api/orgs/{org}/projects/{project}/publish-stats"

    errors = []

    r = requests.get(url)
    r.raise_for_status()

    stats = r.json()

    if last_timestamp_in_minutes is not None and not check_stat_timestamp(stats, last_timestamp_in_minutes):
        print(f"{org}/{project}: Last timestamp is {stats['lastTimestamp']}, which is more than {last_timestamp_in_minutes} minutes ago")
        errors.append(f"{org}/{project}: Last timestamp too long ago")

    if min_messages_prev_hour is not None:
        number_of_messages = int(stats['prevHourCount'])
        if number_of_messages < min_messages_prev_hour:
            print(f"{org}/{project}: Number of messages in previous hour is {number_of_messages}, which is less than {min_messages_prev_hour}")
            errors.append(f"{org}/{project}: Number of messages in previous hour too low")

    if min_messages_prev_minute is not None:
        number_of_messages = int(stats['prevMinuteCount'])
        if number_of_messages < min_messages_prev_minute:
            print(f"{org}/{project}: Number of messages in last minute is {number_of_messages}, which is less than {min_messages_prev_minute}")
            errors.append(f"{org}/{project}: Number of messages in last minute too low")

    print(f"{org}/{project}: Number of errors: {len(errors)}")
    return errors


def main():
    errors = []
    errors += check("adsb", "adsb", last_timestamp_in_minutes=5, min_messages_prev_minute=100)
    errors += check("stefan", "smard", last_timestamp_in_minutes=30, min_messages_prev_hour=100)
    errors += check("stefan", "house", last_timestamp_in_minutes=30, min_messages_prev_hour=10)
    errors += check("finance", "stock-exchange", last_timestamp_in_minutes=30, min_messages_prev_hour=10)

    if len(errors) > 0:
        write_message(", ".join(errors))
        sys.exit(1)

    write_message(f"All checks successful")


if __name__ == "__main__":
    main()
