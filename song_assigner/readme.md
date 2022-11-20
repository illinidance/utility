

# Song Assigner

1. Given a list of youtube URLs (see example_song_list.txt), download them. 
1. Process the songs to get their BPM and meter.
1. Write a file with new playlists built from the songs.

``` python main.py --save_folder output --finput example_song_list.txt --foutput example_song_categories.txt ```

Note ```save_folder``` is optional and a temporary file will be used if it is unspecified. 

Which songs have been downloaded are cached so the command can be repeated if their are errors (assuming ```save_folder``` is used).

The software uses a 10\% threshold for BPM. If this needs to be more or less specific, please change it in ```main.py```.

### Installation: 
```
conda create -n dance python=3.9

conda activate dance

pip install essentia

conda install matplotlib

sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl

sudo chmod a+rx /usr/local/bin/youtube-dl


sudo apt-get install ffmpeg


youtube-dl -x --audio-format mp3 https://www.youtube.com/watch?v=zEcVG7WiGzg
```

