# Illini Dancesport Utilities

## Installation and Dependencies

This project requires the following dependencies to be installed on your system:

- **[Just](https://github.com/casey/just)** – A command runner for executing tasks.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** – A YouTube downloader for extracting audio.
- **[FFmpeg](https://ffmpeg.org/)** – A tool for processing and manipulating audio files.

Please refer to their respective documentation for installation instructions.

After installing the dependencies, verify that they are correctly installed:

```sh
just --version
yt-dlp --version
ffmpeg -version
```

If all commands return version information, you're ready to go.

To use this project, you need to clone the repository and extract essential files into the `data/` directory.

First, clone the repository to your local machine using `git`:

```sh
git clone git@github.com:illinidance/utility.git
cd utility
```

The necessary audio files for announcements and playlists are stored in `playlists/announcement.zip`. You need to extract them into the `data/` folder:

```sh
mkdir -p data
unzip playlist/announcement.zip -d data/
```

After unzipping, the `data/` folder should contain announcement files like:

```sh
utility on main $ ls -al data
.rw-r--r--  57k jy staff 26 Aug  2024 announce_cha_cha.mp3
.rw-r--r--  97k jy staff 26 Aug  2024 announce_foxtrot.mp3
.rw-r--r-- 113k jy staff 26 Aug  2024 announce_jive.mp3
.rw-r--r-- 105k jy staff 26 Aug  2024 announce_quickstep.mp3
.rw-r--r--  81k jy staff 26 Aug  2024 announce_rumba.mp3
.rw-r--r--  49k jy staff 26 Aug  2024 announce_samba.mp3
.rw-r--r-- 105k jy staff 26 Aug  2024 announce_smooth_foxtrot.mp3
.rw-r--r--  65k jy staff 26 Aug  2024 announce_smooth_tango.mp3
.rw-r--r-- 113k jy staff 26 Aug  2024 announce_smooth_viennese_waltz.mp3
.rw-r--r--  49k jy staff 26 Aug  2024 announce_smooth_waltz.mp3
.rw-r--r--  81k jy staff 26 Aug  2024 announce_tango.mp3
.rw-r--r--  49k jy staff 26 Aug  2024 announce_viennese_waltz.mp3
.rw-r--r--  65k jy staff 26 Aug  2024 announce_waltz.mp3

```

These files are required for `just standard-round` and `just latin-round` to work properly.

Now you're all set to generate ballroom dance rounds! 🎵✨

## Rounds file generation

This section outlines the complete workflow for setting up and generating ballroom dance rounds using the `just` commands.

**1. Setup the Project**  
First, clone the repository and extract the required announcement files:

```sh
git clone git@github.com:illinidance/utility.git
cd utility
mkdir -p data
unzip playlists/announcement.zip -d data/
```

**2. Generate Silence (30s Breaks Between Dances)**

Run this command **once** to create a 30-second silence file for breaks between dances:

```sh
just generate-silence 30
```

**3. Download Songs for Each Dance**

Use `just download` to fetch music for all standard and Latin dances. Example commands:

```sh
just download "https://youtube.com/waltz.mp3" waltz
just download "https://youtube.com/tango.mp3" tango
just download "https://youtube.com/viennese_waltz.mp3" viennese_waltz
just download "https://youtube.com/foxtrot.mp3" foxtrot
just download "https://youtube.com/quickstep.mp3" quickstep
just download "https://youtube.com/cha_cha.mp3" cha_cha
just download "https://youtube.com/samba.mp3" samba
just download "https://youtube.com/rumba.mp3" rumba
just download "https://youtube.com/jive.mp3" jive
```

Each song will be saved in `tmp/` and logged in `tmp/log.txt`.

**4. Trim Songs to Desired Length (e.g., 100s Each)**

Use `just trim` to extract a 100-second segment from each song, starting at the 10-second mark:

```sh
just trim tmp/waltz.mp3 10 110
just trim tmp/tango.mp3 10 110
just trim tmp/viennese_waltz.mp3 10 110
just trim tmp/foxtrot.mp3 10 110
just trim tmp/quickstep.mp3 10 110
just trim tmp/cha_cha.mp3 10 110
just trim tmp/samba.mp3 10 110
just trim tmp/rumba.mp3 10 110
just trim tmp/jive.mp3 10 110
```

The starting and ending times may vary for each dance. Adjust as needed.

Trimmed versions will be saved as `tmp/trimmed_<dance>.mp3`.

**5. Generate Dance Round Files**

Once all trimmed songs are ready, generate full dance rounds:

- **Standard Ballroom Round:**
  ```sh
  just standard-round standard_round.mp3
  ```
- **Latin Ballroom Round:**
  ```sh
  just latin-round latin_round.mp3
  ```

**Final Output**

- `tmp/standard_round.mp3` → Complete sequence for Standard dances.
- `tmp/latin_round.mp3` → Complete sequence for Latin dances.

Now you're ready to play full competition-style dance rounds with smooth transitions and announcements!

More details on each command are below.

### Download songs with `just download`

The `just download` command allows you to download an audio file from a given YouTube URL, extract it as an MP3 file, and save it in the `tmp/` directory with the givne output name.

**Usage**

```sh
just download <url> <output>
```

- **`<url>`** – The URL of the video or audio source to download (a YouTube link).
- **`<output>`** – The desired filename without the `.mp3` extension (e.g., 'chacha').

**Example**

To download a waltz file from YouTube:

```sh
just download "https://www.youtube.com/watch?v=fakeurlxxx" waltz
```

This will:

1. Download the video from the given URL.
2. Extract the audio and convert it to an MP3 file.
3. Save it as `tmp/waltz.mp3`.
4. Log the download in `tmp/log.txt` with an entry like:
   ```
   waltz: https://www.youtube.com/watch?v=fakeurlxxx
   ```

Notes

- If a file with the same name already exists in `tmp/`, it will be overwritten.
- You need an active internet connection to download files.
- The download speed and quality depend on `yt-dlp` settings, which use the best available audio by default.

### Trim songs to target length with `just trim`

The `just trim` command extracts a specific portion of an audio file, applies fade-in and fade-out effects, and saves the trimmed version in the `tmp/` directory.

**Usage**

```sh
just trim <input_file> <start_sec> <end_sec>
```

- **`<input_file>`** – Path to the MP3 file to be trimmed.
- **`<start_sec>`** – Start time (in seconds) from which the trim begins.
- **`<end_sec>`** – End time (in seconds) where the trim stops.

**Example**

To trim a waltz song (`tmp/waltz.mp3`) to **100 seconds**, starting from the **10-second mark**:

```sh
just trim tmp/waltz.mp3 10 110
```

This will:

1. Extract the portion of `tmp/waltz.mp3` from **10s to 110s**.
2. Apply:
   - A **2-second fade-in** starting at 10s.
   - A **5-second fade-out** before the end at 105s.
3. Save the result as `tmp/trimmed_waltz.mp3`.

**Notes**

- The output filename is automatically derived from the input file, prefixed with `trimmed_`.
- If the output file already exists, it will be overwritten.
- The fade-in and fade-out effects ensure smooth transitions in trimmed clips.

### Generate silence with `just generate-silence`

The `just generate-silence` command creates a silent MP3 file of a specified duration. This silence is used as a break between dances in the ballroom round audio sequences.

**Usage**

```sh
just generate-silence <duration_s>
```

- **`<duration_s>`** – The length of the silence file in seconds.

**Example**

To generate **30 seconds** of silence:

```sh
just generate-silence 30
```

This will create a file `tmp/silence.mp3` that contains 30 seconds of silence.

**Notes**

- This command **only needs to be run once** for any given duration.
- If the silence file already exists in `tmp/`, you do not need to regenerate it unless you want a different duration.
- The generated silence file is used automatically in `just standard-round` and `just latin-round` to insert breaks between dances.

### Generating Dance Rounds with `just standard-round` and `just latin-round`

The `just standard-round` and `just latin-round` commands create a full ballroom dance round by concatenating announcements, trimmed dance tracks, and silent breaks between dances.

#### Standard Round

The `just standard-round` command generates a **standard round**, which consists of:

1. A spoken announcement for each dance.
2. The corresponding trimmed dance track.
3. A silence break between each dance.

**Usage**

```sh
just standard-round <output_file>
```

- **`<output_file>`** – The name of the output MP3 file (saved in `tmp/`).

**Example**

```sh
just standard-round standard_round.mp3
```

This will create `tmp/standard_round.mp3`, containing the following sequence:

- Announcement → Waltz → Silence
- Announcement → Tango → Silence
- Announcement → Viennese Waltz → Silence
- Announcement → Foxtrot → Silence
- Announcement → Quickstep

#### Latin Round

The `just latin-round` command generates a **Latin ballroom dance round**, with the same structure as the Standard round but using Latin dances.

**Usage**

```sh
just latin-round <output_file>
```

- **`<output_file>`** – The name of the output MP3 file (saved in `tmp/`).

**Example**

```sh
just latin-round latin_round.mp3
```

This will create `tmp/latin_round.mp3`, containing the following sequence:

- Announcement → Cha-Cha → Silence
- Announcement → Samba → Silence
- Announcement → Rumba → Silence
- Announcement → Jive

**Prerequisites**

Before running these commands, ensure that:

- The required **announcement files** are extracted into `data/` (see [Setup Instructions](#installation-and-dependencies)).
- The **trimmed dance tracks** exist in `tmp/` (see [Trimming Audio](#trim-songs-to-target-length-with-just-trim)).
- A **silence file** has been generated (see [Generating Silence](#generate-silence-with-just-generate-silence)).

Now you can easily generate complete ballroom dance rounds for practice, training, or competitions!

---

<!--## Sync Event Service Space Request Confirmation with Google Calendar-->
<!---->
<!--[cal.py](cal.py)-->
<!---->
<!--Please refer to [Google Calendar Python-->
<!--Quickstart](https://developers.google.com/calendar/api/quickstart/python) for-->
<!--Authorization setup.-->
<!---->
<!--## Google Contact Sync-->
<!---->
<!--[contacts.py](contacts.py)-->
<!---->
<!--## Generate Rounds File-->
<!---->
<!--### Preparation-->
<!---->
<!--Unzip announcement `mp3`s:-->
<!---->
<!--```bash-->
<!--unzip playlists/announcements.zip -d playlists/-->
<!--```-->
<!---->
<!--Generate a 30s silence `mp3`:-->
<!---->
<!--```bash-->
<!--python rounds.py silence --duration=30-->
<!--mv silence.mp3 playlists/-->
<!--```-->
<!---->
<!--### Define playlists and generate rounds files-->
<!---->
<!--Define your playlist in a `.ini` file. See files in [playlists](playlists) for examples.-->
<!---->
<!--Then run `python3 rounds.py run <your_playlist>.ini` to download, trim and concatenate songs into one round file.-->
<!---->
<!--For example, running-->
<!---->
<!--```bash-->
<!--python3 rounds.py run playlists/standard_1.ini-->
<!--```-->
<!---->
<!--will produce a standard rounds file `standard_1.mp3` in `playlists/`.-->
