_default:
    @just --list

_mk_tmp_dir:
    @mkdir -p tmp/

# download the URL to as an mp3 file and save to tmp/`output`
download url output: _mk_tmp_dir
    rm -f tmp/"{{ output }}.mp3"
    yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 {{ url }} -o tmp/"{{ output }}.mp3"
    echo "{{ output }}": "{{ url }}" >> tmp/log.txt

# Generate a silent mp3 file of `duration_s` seconds
generate-silence duration_s: _mk_tmp_dir
    ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -t {{ duration_s }} tmp/silence.mp3

# trim the input mp3 file using the start and end timestamp
trim input_file start_sec end_sec:
    ffmpeg -y -i {{ input_file }} \
        -map a -ss {{ start_sec }} \
        -to {{ end_sec }} \
        -af afade=t=in:st={{ start_sec }}:d=2,afade=t=out:st=$(({{ end_sec }}-5)):d=5 \
        tmp/trimmed_{{ file_name(input_file) }}

clean:
    rm tmp/*.mp3

standard-round output_file:
    ffmpeg \
        -i data/announce_waltz.mp3 \
        -i tmp/trimmed_waltz.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_tango.mp3 \
        -i tmp/trimmed_tango.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_viennese_waltz.mp3 \
        -i tmp/trimmed_viennese_waltz.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_foxtrot.mp3 \
        -i tmp/trimmed_foxtrot.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_quickstep.mp3 \
        -i tmp/trimmed_quickstep.mp3 \
        -filter_complex [0:a:0][1:a:0][2:a:0][3:a:0][4:a:0][5:a:0][6:a:0][7:a:0][8:a:0][9:a:0][10:a:0][11:a:0][12:a:0][13:a:0]concat=n=14:v=0:a=1[outa] \
        -map [outa] \
        tmp/{{ output_file }}

latin-round output_file:
    ffmpeg \
        -i data/announce_cha_cha.mp3 \
        -i tmp/trimmed_cha_cha.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_samba.mp3 \
        -i tmp/trimmed_samba.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_rumba.mp3 \
        -i tmp/trimmed_rumba.mp3 \
        -i tmp/silence.mp3 \
        -i data/announce_jive.mp3 \
        -i tmp/trimmed_jive.mp3 \
        -filter_complex [0:a:0][1:a:0][2:a:0][3:a:0][4:a:0][5:a:0][6:a:0][7:a:0][8:a:0][9:a:0][10:a:0]concat=n=11:v=0:a=1[outa] \
        -map [outa] \
        tmp/{{ output_file }}
