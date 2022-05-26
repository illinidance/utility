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

    # E.g.: "Tuesday, June 7, 2022"
    date_pattern = re.compile(r"\w+, \w+ \d+, \d{4}")
    # E.g.: "7:00 PM - 10:00 PM Illini Dancesport Practice Space (Tentative 4/1/2022)"
    time_pattern = re.compile(r"\d+:\d+ [AP]M - \d+:\d+ [AP]M")
    # TODO: Better location handling. Currently the location is hardcoded. The
    # difficultly comes from line breaking. Sometimes the location, e.g., "314A"
    # will be in the same line as the `time_pattern`. But sometime it's on a
    # new line.
    location_pattern = re.compile(
        r"314A|314B|Ballroom|Room A\b|Room B\b|Room C\b|Multipurpose"
    )

    # filter out noise lines and only keep lines that contain the (1) date, (2)
    # the time or (3) the location of an event.
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
        else:
            # ignore noise line
            continue
    filtered_text = filtered_text.strip()

    # E.g.: "Sunday, June 12, 2022 7:00 PM - 10:00 PM Illini Dancesport Practice Space (Tentative 4/1/2022) 314A"
    #   date: Sunday, June 12, 2022
    #   time: 7:00 PM - 10:00 PM
    #   event_name: Illini Dancesport Practice Space
    #   status: Tentative 4/1/2022
    #   location: 314A
    pattern = re.compile(
        r"(?P<date>\w+, \w+ \d+, \d{4}) (?P<time>\d+:\d+ [AP]M - \d+:\d+ [AP]M) (?P<event_name>.*) \((?P<status>.*)\) (?P<location>.*)"
    )

    events = [make_event_dict(m.groupdict()) for m in pattern.finditer(filtered_text)]
    return events


def to_localized_isoformat(m_date: str, m_time: str) -> Dict[str, str]:
    """Convert time str to dict with ISO format time str and timezone info."""
    time_fmt = "%I:%M %p, %A, %B %d, %Y"
    # "7:00 PM, Tuesday, May 17, 2022"
    tz = timezone("US/Central")
    m_t = f"{m_date.strip()}, {m_time.strip()}"
    m_t = datetime.datetime.strptime(m_t, time_fmt)
    m_t = tz.localize(m_t)
    # "2022-05-17T19:00:00-05:00"
    m_t = m_t.isoformat()
    # {"dateTime": "2022-05-17T19:00:00-05:00", "timeZone": "US/Central"}
    return {"dateTime": m_t, "timeZone": str(tz)}


def make_event_dict(m: Dict, location_prefix="Illini Union") -> Dict:
    """Convert the input dictionary into a form accepted by the Google Calendar API."""
    # start and end time
    start_time, end_time = tuple(m["time"].split("-"))
    start_time = to_localized_isoformat(m["date"], start_time)
    end_time = to_localized_isoformat(m["date"], end_time)

    return {
        "summary": f"{m['event_name']} ({m['status']})",
        "location": f"{location_prefix} {m['location']}",
        "start": start_time,
        "end": end_time,
    }


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def update_calendar(events: List[Dict]):
    """Update the team's Google Calendar with given events."""
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
