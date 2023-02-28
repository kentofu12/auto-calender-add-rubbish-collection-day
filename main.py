from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("URL")
TIMETREE_ENDPOINT = os.getenv("TIMETREE_ENDPOINT")
TIMETREE_TOKEN = os.getenv("TIMETREE_TOKEN")


def add_event(emoji, event_day):
    headers = {
        "accept": "application/vnd.timetree.v1+json",
        "authorization": f"Bearer {TIMETREE_TOKEN}"
    }

    body = {
        'data': {
            'attributes': {
                'title': f'今晩ゴミ出し！{emoji}',
                'category': 'schedule',
                'all_day': True,
                'start_at': event_day,
                'start_timezone': 'Pacific/Auckland',
                'end_at': event_day,
                'end_timezone': 'Pacific/Auckland',
            },
            'relationships': {
                'label': {
                    'data': {
                        'id': 'ao8qCU0jL-el,4',
                        'type': 'label'
                    }
                }
            }
        }
    }

    event_response = requests.post(url=TIMETREE_ENDPOINT, json=body, headers=headers)
    print(event_response.text)


response = requests.get(url=URL)
soup = BeautifulSoup(response.text, "html.parser")

rubbish_day = soup.find(class_="links").find(class_="m-r-1").text
rubbish_type = ""

for icon in soup.find(class_="links").find_all(class_="sr-only"):
    if icon.text == "Rubbish":
        rubbish_type += "🗑"
    elif icon.text == "Recycle":
        rubbish_type += "♻️"

today_year = datetime.now().year
day_before_rubbish_day = datetime.strptime(rubbish_day, "%A %d %B") - timedelta(days=1)
format_day_before_rubbish_day = datetime.strftime(day_before_rubbish_day, f"{today_year}-%m-%dT%H:%M:%SZ")

try:
    with open("last_entry.txt", "r") as file:
        last_entry = file.read()

except FileNotFoundError:
    with open("last_entry.txt", "w") as file:
        file.write(f"{format_day_before_rubbish_day}")
        add_event(rubbish_type, format_day_before_rubbish_day)

else:
    if last_entry != format_day_before_rubbish_day:
        add_event(rubbish_type, format_day_before_rubbish_day)
        with open("last_entry.txt", "w") as file:
            file.write(f"{format_day_before_rubbish_day}")
