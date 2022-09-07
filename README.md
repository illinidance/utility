# Illini Dancesport Utilities

## Sync Event Service Space Request Confirmation with Google Calendar

This is a script to synchronize Illini Dancesport's Google Calendar with the input space request confirmation PDF from Illini Union Event Service.
It parses the PDF, extracts times and locations, and uses Google Calendar API to create or update events.

Please refer to [Google Calendar Python
Quickstart](https://developers.google.com/calendar/api/quickstart/python) for
Authorization setup.

## Google Contact Sync

TODO

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

Make round playlist. See [standard_rounds.txt](standard_rounds.txt) as an example.

Create rounds music file using the playlist:

```bash
python3 rounds.py concat <playlist>
```
