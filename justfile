_default:
    @just --list

download url:
    yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 {{url}}
