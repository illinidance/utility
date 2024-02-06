import configparser
import pathlib
import re
import subprocess
from shutil import which

import click

assert which("ffmpeg") is not None
assert which("lame") is not None
assert which("youtube-dl") is not None
assert which("say") is not None


@click.group()
def cli():
    pass


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=pathlib.Path))
@click.option("--start_sec", default=0, type=int)
def trim(input_file: pathlib.Path, start_sec: int) -> None:
    _ = _trim(input_file, start_sec)


def _trim(input_file: pathlib.Path, start_sec: int) -> pathlib.Path:
    assert input_file.suffix.lower() == ".mp3"
    trimmed_file = input_file.parent / (
        "trimmed_"
        + "_".join(x for x in re.split(r"[ '_\-\(\)]+", input_file.stem) if x != "")
        + input_file.suffix
    )
    end_sec = start_sec + 100
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),
            "-map",
            "a",
            "-ss",
            str(start_sec),
            "-to",
            str(end_sec),
            "-af",
            f"afade=t=in:st={start_sec}:d=2,afade=t=out:st={end_sec-5}:d=5",
            str(trimmed_file),
        ]
    )
    return trimmed_file


@click.command()
@click.argument("dance", type=str)
def announce(dance: str):
    out_aiff = f"announce_{dance}.aiff"
    out_mp3 = f"announce_{dance}.mp3"
    subprocess.run(["say", f'"Your next dance: {dance}"', "-o", out_aiff])
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            out_aiff,
            "-f",
            "mp3",
            "-acodec",
            "libmp3lame",
            "-ab",
            "192000",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-b:a",
            "128k",
            out_mp3,
        ]
    )
    subprocess.run(["rm", out_aiff])


@click.command()
@click.option("--duration", default=30, type=int)
def silence(duration: int):
    # ffprobe -select_streams a -show_streams <mp3>
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-t",
            str(duration),
            "silence.mp3",
        ]
    )


@cli.command()
@click.argument("rounds_file", type=click.Path(exists=True, path_type=pathlib.Path))
def concat(rounds_file: pathlib.Path):
    _concat(rounds_file)


def _concat(rounds_file: pathlib.Path, output_file=None):
    if output_file == None:
        output_file = rounds_file.with_suffix(".mp3")
    with open(rounds_file) as f:
        rounds = [x.strip() for x in f.readlines()]
    n = len(rounds)
    filter_complex = ""
    for i in range(n):
        filter_complex += f"[{i}:a:0]"
    filter_complex += f"concat=n={n}:v=0:a=1[outa]"
    cmd = ["ffmpeg"]
    for x in rounds:
        cmd.append("-i")
        cmd.append(x)
    cmd.extend(["-filter_complex", filter_complex, "-map", "[outa]", str(output_file)])
    print(" ".join(cmd))
    subprocess.run(cmd)


@cli.command()
@click.argument("url", type=str)
@click.option("-d", "--dest", type=str, default=None)
def download(url: str, dest: str):
    _download(url, dest)


def _download(url: str, dest: str) -> None:
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        url,
    ]
    if dest:
        cmd.append("--output")
        cmd.append(dest)
    subprocess.run(cmd)


@cli.command()
@click.argument("rounds_file", type=click.Path(exists=True, path_type=pathlib.Path))
@click.option("-r", "--resume", is_flag=True, default=False)
def run(rounds_file: pathlib.Path, resume: bool):
    playlist_dir = pathlib.Path("playlists")
    assert playlist_dir.exists()

    config = configparser.ConfigParser()
    config.read(rounds_file)
    output_txt = pathlib.Path("./tmp_rounds.txt")
    output_mp3 = rounds_file.with_suffix(".mp3")
    sequence = []
    for sec in config.sections():
        url = config[sec]["url"]
        start_sec = int(config[sec].get("start_sec", "0"))
        mp3_file = playlist_dir / f"original_{sec}.mp3"
        announce_mp3_file = playlist_dir / f"announce_{sec}.mp3"
        silence_mp3_file = playlist_dir / "silence.mp3"

        # download the music
        if not resume and mp3_file.exists() is False:
            # _download(url, str(mp3_file.with_suffix(".audio")))
            _download(url, str(mp3_file))

        # trim the music
        trimmed_mp3_file = _trim(mp3_file, start_sec)

        # add to playlist
        sequence.append(str(announce_mp3_file))
        sequence.append(str(trimmed_mp3_file))
        sequence.append(str(silence_mp3_file))

    if sequence[-1].endswith("silence.mp3"):
        sequence.pop()

    with open(output_txt, "w") as f:
        for s in sequence:
            f.write(f"{s}\n")

    _concat(output_txt, output_mp3)


cli.add_command(trim)
cli.add_command(announce)
cli.add_command(silence)
cli.add_command(concat)
cli.add_command(download)

if __name__ == "__main__":
    cli()
