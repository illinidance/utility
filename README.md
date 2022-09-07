# Illini Dancesport Utilities

## Sync Event Service Space Request Confirmation with Google Calendar

[pdf_to_google_calendar.py](pdf_to_google_calendar.py)

Please refer to [Google Calendar Python
Quickstart](https://developers.google.com/calendar/api/quickstart/python) for
Authorization setup.

## Google Contact Sync

[contacts.py](contacts.py)

## Generate Rounds file

Download mp3 from YouTube:

```bash
python3 rounds.py download <url>
```

Trim the mp3 file to 100 sec (optional: select start sec):

```bash
python3 rounds.py trim <mp3_file> --start_sec=0
```

Generate 30s silence as break between dances (optional: set length of silence):

```bash
python3 rounds.py silence --duration=30
```

Generate announcement before dance:

```bash
python3 rounds.py announce waltz
python3 rounds.py announce tango
python3 rounds.py announce foxtrot
python3 rounds.py announce quickstep
python3 rounds.py announce viennese_waltz
```

Create a rounds playlist. See [standard_rounds.txt](standard_rounds.txt) as an example.

Concatenate songs in the playlist to create the rounds music file:

```bash
python3 rounds.py concat <playlist>
```
