from datetime import datetime
import json


data = None

LAST_READ = datetime(1, 1, 1, 0, 0, 0)
SETTINGS_PATH = "settings.json"


def loadSettings():
    global LAST_READ, data, SETTINGS_PATH

    now = datetime.now()
    duration_in_s = (now - LAST_READ).total_seconds()
    minutes = divmod(duration_in_s, 60)[0]

    if minutes >= 5:
        f = open(SETTINGS_PATH)
        data = json.load(f)
        convertData()
        LAST_READ = now
        print("Loaded json:", data)
        f.close()
    else:
        print("Returning old json.")


def convertData():
    if isinstance(data["api_limit"], str):
        data["api_limit"] = None
