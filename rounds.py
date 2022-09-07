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
    output_file = rounds_file.with_suffix(".mp3")
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-i",
            str(rounds_file),
            "-c",
            "copy",
            str(output_file),
        ]
    )


@cli.command()
@click.argument("url", type=str)
def download(url: str):
    subprocess.run(
        ["youtube-dl", "-x", "--embed-thumbnail", "--audio-format", "mp3", url]
    )


cli.add_command(trim)
cli.add_command(announce)
cli.add_command(silence)
cli.add_command(concat)
cli.add_command(download)

if __name__ == "__main__":
    cli()
