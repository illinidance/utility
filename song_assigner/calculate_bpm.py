import essentia

import essentia.standard as es

import matplotlib.pyplot as plt

from tempfile import TemporaryDirectory


def get_bpm(mp3_file="NIGHTCORE - She thinks my tractor's sexy-zEcVG7WiGzg.mp3"):
    loader = es.MonoLoader(filename=mp3_file)

    audio = loader()

    rhythm_extractor = es.RhythmExtractor2013(method="degara")

    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

    return bpm


def get_meter(mp3_file="NIGHTCORE - She thinks my tractor's sexy-zEcVG7WiGzg.mp3"):
    loader = es.MonoLoader(filename=mp3_file)

    audio = loader()

    rhythm_extractor = es.RhythmExtractor2013(method="degara")
    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

    beatsLoudness = es.BeatsLoudness(beats=beats)
    beatogram = es.Beatogram()
    meter = es.Meter()

    loudness, loudnessBandRatio = beatsLoudness(audio)

    bg = beatogram(loudness, loudnessBandRatio)
    m = meter(bg)

    return m


if __name__ == "__main__":
    bpm = get_bpm()
    print(bpm)

    meter = get_meter()
    print(meter)
