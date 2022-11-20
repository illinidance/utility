


import essentia

import essentia.standard as es

import matplotlib.pyplot as plt

from tempfile import TemporaryDirectory

def get_bpm(mp3_file = 'NIGHTCORE - She thinks my tractor\'s sexy-zEcVG7WiGzg.mp3'):
    loader = es.MonoLoader(filename=mp3_file)

    audio = loader()


    #novelty_curve = es.NoveltyCurve()

    rhythm_extractor = es.RhythmExtractor2013(method="degara")

    #bpm_histo = es.BpmHistogram()

    #histo = bpm_histo(novelty_curve(audio))


    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

    #marker = es.AudioOnsetsMarker(onsets=beats, type='beep')
    #marked_audio = marker(audio)


    #Use this to record a version with beats
    #temp_dir = TemporaryDirectory()
    #es.MonoWriter(filename=temp_dir.name + '/out.flac')(marked_audio)
    #print(temp_dir.name)
    
    #plt.figure()
    #plt.plot(audio)
    #for beat in beats:
    #    plt.axvline(x=beat*44100, color='red')
    #plt.xlabel('Time (samples)')
    #plt.title("Audio waveform and the estimated beat positions")
    #plt.savefig('tmp.png')

    return bpm


def get_meter(mp3_file = 'NIGHTCORE - She thinks my tractor\'s sexy-zEcVG7WiGzg.mp3'):
    loader = es.MonoLoader(filename=mp3_file)

    audio = loader()

    '''
    rhythm_extractor = es.RhythmExtractor2013(method="degara")
    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

    od1 = es.OnsetDetection(method='hfc')
    od2 = es.OnsetDetection(method='complex')
    
    w = es.Windowing(type = 'hann')
    fft = es.FFT() # this gives us a complex FFT
    c2p = es.CartesianToPolar() # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()

    # Computing onset detection functions.
    for frame in es.FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.hfc', od1(mag, phase))
        pool.add('features.complex', od2(mag, phase))

    onsets = es.Onsets()
    
    onsets_hfc = onsets(# this algo expects a matrix, not a vector
                    essentia.array([ pool['features.hfc'] ]),
                    # you need to specify weights, but as there is only a single
                    # function, it doesn't actually matter which weight you give it
                    [ 1 ])
    '''
    
    rhythm_extractor = es.RhythmExtractor2013(method="degara")
    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)
    
    beatsLoudness = es.BeatsLoudness(beats = beats)
    beatogram = es.Beatogram()
    meter = es.Meter()
    
    loudness, loudnessBandRatio = beatsLoudness(audio)
    #print(loudness, loudnessBandRatio)
    bg = beatogram(loudness, loudnessBandRatio)
    #print(bg)
    m = meter(bg)
    #print(ts)
    

    return m


if __name__ == '__main__':
    bpm = get_bpm()
    print(bpm)
    
    meter = get_meter()
    print(meter)