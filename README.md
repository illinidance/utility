# Illini Dancesport Utilities

## Sync Event Service Space Request Confirmation with Google Calendar

[cal.py](cal.py)

Please refer to [Google Calendar Python
Quickstart](https://developers.google.com/calendar/api/quickstart/python) for
Authorization setup.

## Google Contact Sync

[contacts.py](contacts.py)

## Generate Rounds File

Define your round in a `.ini` file. See files in [playlists](playlists) for examples.

Compile and generate the round file:

```bash
python3 rounds.py run playlists/standard_1.ini
```

which will produce a standard rounds file `standard_1.mp3` in `playlists/`.
