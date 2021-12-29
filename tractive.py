import json
import requests
import logging
import os
from datetime import datetime, timedelta

# Settings
API_URL         = os.getenv('TRACTIVE_API_URL', 'https://graph.tractive.com/3')
TRACTIVE_CLIENT = os.getenv('TRACTIVE_CLIENT', '5f9be055d8912eb21a4cd7ba')
CACHE_FILE      = os.getenv('TRACTIVE_CACHE', '/tmp/tractive.cache')
OUTPUT_FILE     = os.getenv('TRACTIVE_OUTPUT', '/tmp/tractive.data')


DEBUG = os.getenv('TRACTIVE_DEBUG', 'None')
if DEBUG == "None":
    DEBUG = False

class TractiveTracker:

    def __init__(self) -> None:
        self._user_credentials = None
        self._tracker_ids = []
        self._tracker_data = []


    def init(self):
        if not self.get_cached_user_credentials():
            if not self.get_user_credentials():
                return False

        self.get_trackers()
        self.get_tracker_data()
        self.write_data()
        

    # Check if credentials are cached and still valid
    def get_cached_user_credentials(self):
        now = int(datetime.timestamp(datetime.now()))
        if os.path.isfile(CACHE_FILE):
            f = open(CACHE_FILE, "r")
            data = json.load(f)
            
            if 'access_token' in data:
                if data["expires_at"] > now:
                    self._user_credentials = data
                    if DEBUG:
                        print("Cache: HIT")

                    return True

        if DEBUG:
            print("Cache: MISS")

        return False


    # Writing data
    def write_data(self):
        f = open(OUTPUT_FILE, "w")

        f.write(f"# HELP TractiveTracker_battery Last reported battery level in procent\n")
        f.write(f"# TYPE TractiveTracker_battery gauge\n")
        for tracker in self._tracker_data:
            tracker_id      = tracker["_id"]
            tracker_battery = tracker["battery_level"]
            tracker_status  = tracker["hw_status"]
            f.write(f"TractiveTracker_battery{{tracker=\"{tracker_id}\"}} {tracker_battery}\n")

        now = int(datetime.timestamp(datetime.now()))
        f.write(f"\n")
        f.write(f"# HELP TractiveTracker_status Last update timestamp\n")
        f.write(f"# TYPE TractiveTracker_status counter\n")
        f.write(f"TractiveTracker_status {now}\n")

        f.close()
        return True


    # Get user credentials
    def get_user_credentials(self):
        if DEBUG:
            print("-> Getting credentials")

        headers = {
            "x-tractive-client": X_TRACTIVE_CLIENT,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
        }

        tractive_username = os.environ.get('TRACTIVE_USER')
        tractive_password = os.environ.get('TRACTIVE_PASS')

        resp = requests.post(
            f"{API_URL}/auth/token",
            data=json.dumps(
                {
                    "platform_email": tractive_username,
                    "platform_token": tractive_password,
                    "grant_type": "tractive",
                }
            ),
            headers=headers,
        )

        if resp.status_code != 200:
            print(f"Error: credentials")
            print(resp.content)
            return False

        # Write content to cache
        f = open(CACHE_FILE, "w")
        f.write(resp.content.decode("utf-8"))
        f.close()

        self._user_credentials = resp.json()

        return True


    # Get Trackers
    def get_trackers(self):
        headers = {
            "x-tractive-client": X_TRACTIVE_CLIENT,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-tractive-user": self._user_credentials["user_id"],
            "authorization": f"Bearer {self._user_credentials['access_token']}",
        }

        resp = requests.get(
            f"{API_URL}/user/{self._user_credentials['user_id']}/trackers",
            headers=headers,
        )

        if resp.status_code != 200:
            print("Error: tracers")
            print(resp.content)
            exit

        result = resp.json()
        for tracker in result:
            self._tracker_ids.append(tracker["_id"])
        
        return True


    # Get tracker data
    def get_tracker_data(self):
        headers = {
            "x-tractive-client": X_TRACTIVE_CLIENT,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-tractive-user": self._user_credentials["user_id"],
            "authorization": f"Bearer {self._user_credentials['access_token']}",
        }

        for tracker_id in self._tracker_ids:
            hw_report = []

            resp = requests.get(
                f"{API_URL}/device_hw_report/{tracker_id}/",
                headers=headers,
            )

            if resp.status_code != 200:
                print(f"Error: tracker {tracker_id}")
                print(resp.content)
                exit

            hw_report = resp.json()

            self._tracker_data.append(hw_report)

        return True



scanner = TractiveTracker()
scanner.init()