import datetime
import os
import re
import sys
from typing import Dict
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pdfminer.high_level import extract_text
from pytz import timezone


def parse_pdf(pdf_file: str) -> List[Dict]:
    text = extract_text(pdf_file)

    date_pattern = re.compile(r"\w+, \w+ \d+, \d{4}")
    time_pattern = re.compile(r"\d+:\d+ [AP]M - \d+:\d+ [AP]M")
    location_pattern = re.compile(
        r"314A|314B|Ballroom|Room A\b|Room B\b|Room C\b|Multipurpose"
    )

    filtered_text = ""
    for s in text.splitlines():
        if date_pattern.match(s):
            # every new event starts with the date in the format of "Sunday, August 7, 2022"
            filtered_text += "\n"
            filtered_text += s.strip()
        elif time_pattern.match(s) or location_pattern.search(s):
            # followed by time "7:00 PM - 10:00 PM", event name "Illini
            # Dancesport Practice Space (Starting after Aug 4. 2022)" and
            # location "314B". But sometimes this line could be wrapped, causing
            # the location name to be line-broken in the middle. So we have to
            # use `.search()` instead of `.match()`. Refer to python `re`
            # library document for the difference.
            filtered_text += " "
            filtered_text += s.strip()
    filtered_text = filtered_text.strip()

    pattern = re.compile(
        r"(?P<date>\w+, \w+ \d+, \d{4}) (?P<time>\d+:\d+ [AP]M - \d+:\d+ [AP]M) (?P<event_name>.*) \((?P<status>.*)\) (?P<location>.*)"
    )

    events = [m.groupdict() for m in pattern.finditer(filtered_text)]

    events = [make_event_dict(m) for m in events]
    return events


def make_event_dict(m: Dict, location_prefix="Illini Union") -> Dict:
    """Convert the input dictionary into a form accepted by the Google Calendar API."""
    # start and end time
    time_fmt = "%I:%M %p, %A, %B %d, %Y"
    central = timezone("US/Central")

    start_time, end_time = tuple(m["time"].split("-"))
    start_time = start_time.strip() + ", " + m["date"]
    end_time = end_time.strip() + ", " + m["date"]
    start_time = datetime.datetime.strptime(start_time, time_fmt)
    end_time = datetime.datetime.strptime(end_time, time_fmt)
    start_time = central.localize(start_time)
    end_time = central.localize(end_time)

    return {
        "summary": f"{m['event_name']} ({m['status']})",
        "location": f"{location_prefix} {m['location']}",
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": str(central),
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": str(central),
        },
    }


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def update_calendar(events: List[Dict]):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        for event in events:

            # check if it already exists
            existing_events = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=event["start"]["dateTime"],
                    timeMax=event["end"]["dateTime"],
                    singleEvents=True,
                )
                .execute()
            )
            event_id = None
            for e in existing_events.get("items", []):
                if e["summary"] == event["summary"]:
                    event_id = e["id"]

            # update if exists, or create new
            if event_id == None:
                print(f"Creating: {event}")
                event = (
                    service.events().insert(calendarId="primary", body=event).execute()
                )
            else:
                print(f"Updating: {event}")
                event = (
                    service.events()
                    .update(calendarId="primary", eventId=event_id, body=event)
                    .execute()
                )

    except HttpError as error:
        print("An error occurred: %s" % error)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {os.path.basename(__file__)} <confirmation_pdf>")
        exit(1)
    pdf_file = sys.argv[1]
    events = parse_pdf(pdf_file)
    update_calendar(events)
