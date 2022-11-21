import os.path as osp

from calculate_bpm import get_bpm, get_meter

from get_youtube import parse_file, download_youtube

import argparse
import os
import os.path as osp

from collections import defaultdict

from tempfile import TemporaryDirectory


tempos = {
    "standard": {
        "waltz": 87,
        "tango": 64,
        "Viennese waltz": 174,
        "foxtrot": 112,
        "quickstep": 200,
    },
    "latin": {
        "cha cha": 124,
        "samba": 100,
        "rumba": 104,
        "paso doble": 110,
        "jive": 172,
    },
    "smooth": {
        "waltz": 90,
        "tango": 60,
        "Viennese waltz": 159,
        "foxtrot": 120,
        "peabody": 240,
    },
    "rhythm": {
        "cha cha": 120,
        "swing": 140,
        "rumba": 124,
        "bolero": 88,
        "mambo": 188,
        "samba": 100,
        "merengue": 60,
        "paso doble": 110,
        "WC swing": 120,
        "polka": 120,
        "hustle": 120,
    },
}

beats_per_measure = {
    "standard": {
        "waltz": 3,
        "tango": 2,
        "Viennese waltz": 3,
        "foxtrot": 4,
        "quickstep": 4,
    },
    "latin": {"cha cha": 4, "samba": 2, "rumba": 4, "paso doble": 2, "jive": 4},
    "smooth": {"waltz": 3, "tango": 2, "Viennese waltz": 3, "foxtrot": 4, "peabody": 4},
    "rhythm": {
        "cha cha": 4,
        "swing": 4,
        "rumba": 4,
        "bolero": 4,
        "mambo": 4,
        "samba": 2,
        "merengue": 2,
        "paso doble": 2,
        "WC swing": 4,
        "polka": 2,
        "hustle": 4,
    },
}


def classify_song(bpm, meter, name, categories, threshold=0.1):

    for style in tempos:
        for dance in tempos[style]:
            tempo_min = tempos[style][dance] * (1 - threshold)
            tempo_max = tempos[style][dance] * (1 + threshold)

            smeter = beats_per_measure[style][dance]

            # assume that multiples of 2 are the same for meter
            if (
                bpm > tempo_min
                and bpm < tempo_max
                and (smeter == meter or 2 * smeter == meter or smeter == 2 * meter)
            ):
                categories[style + " " + dance].append(name)


def classify_song_from_file(file_name, threshold=0.1):

    styles = []

    bpm = get_bpm(file_name)
    meter = get_meter(file_name)

    for style in tempos:
        for dance in tempos[style]:
            tempo_min = tempos[style][dance] * (1 - threshold)
            tempo_max = tempos[style][dance] * (1 + threshold)

            smeter = beats_per_measure[style][dance]

            # assume that multiples of 2 are the same for meter
            if (
                bpm > tempo_min
                and bpm < tempo_max
                and (smeter == meter or 2 * smeter == meter or smeter == 2 * meter)
            ):

                styles.append(style + " " + dance)
    return styles


tab = "\t"


def print_categories(categories, out_file):
    with open(out_file, "w") as f:
        for key in categories:
            f.write(key + ":" + "\n")
            for name in categories[key]:
                f.write(tab + name + "\n")
            f.write("\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--save_folder",
        type=str,
        default=None,
        help="Directory to save downloaded songs. Don't use for a temporary directory.",
    )
    parser.add_argument(
        "--finput",
        type=str,
        default="example_song_list.txt",
        help="The input URL file.",
    )
    parser.add_argument(
        "--foutput",
        type=str,
        default="example_song_list_categories.txt",
        help="The output txt file.",
    )

    parser.add_argument("--whatever", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    if args.save_folder != None and osp.exists(args.save_folder):
        print("Save folder already exists! Using that folder.")
        store_dir = args.save_folder

        urls = parse_file(args.finput)
        download_youtube(urls, store_dir)
    else:
        if args.save_folder != None:
            os.makedirs(args.save_folder, exist_ok=True)

            store_dir = args.save_folder
        else:
            temp_dir = TemporaryDirectory()
            store_dir = temp_dir.name

        urls = parse_file(args.finput)

        download_youtube(urls, store_dir)

    file_names = [
        f for f in os.listdir(store_dir) if osp.isfile(osp.join(store_dir, f))
    ]
    file_names.remove("downloaded.txt")

    song_names = [osp.splitext(f)[0] for f in file_names]

    bpms = [get_bpm(osp.join(store_dir, fn)) for fn in file_names]

    meters = [get_meter(osp.join(store_dir, fn)) for fn in file_names]

    print("Names:", song_names)
    print("BPMs:", bpms)
    print("Meters:", meters)

    categories = defaultdict(list)

    for bpm, meter, name in zip(bpms, meters, song_names):
        classify_song(bpm, meter, name, categories)

    print_categories(categories, args.foutput)
