from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
import io, base64
import librosa
import librosa.display
from sklearn.preprocessing import LabelEncoder
from keras.models import load_model
from scipy.io import wavfile
import pandas as pd
from tensorflow.keras.initializers import glorot_uniform

def Amplitude(path):
    """ Gives the Amplitude Time Graph of the Audio"""
    sound = AudioSegment.from_wav(path)
    sound_samples = sound.get_array_of_samples()
    samp_freq = sound.frame_rate

    speech_samples_norm = np.array(sound_samples) / np.max(np.array(sound_samples))


    strt_samp = 0
    end_samp = len(speech_samples_norm)
    end_ms = len(speech_samples_norm) / samp_freq

    xrange = np.linspace(0, end_ms, end_samp - strt_samp)

    plt.switch_backend('AGG')
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(xrange, speech_samples_norm)
    ax.set_title('Amplitude Graph')
    ax.set_ylabel("Amplitude")
    ax.set_xlabel('Time in seconds')
    ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
    plt.close('all')
    flike = io.BytesIO()
    fig.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    return b64



def spectogram(path):
    """ Gives the Spectogram Graph of the Audio"""
    sound = AudioSegment.from_wav(path)
    sound_samples = sound.get_array_of_samples()
    samp_freq = sound.frame_rate

    speech_samples_norm = np.array(sound_samples) / np.max(np.array(sound_samples))

    strt_samp = 0
    end_samp = len(speech_samples_norm)

    winlen = int(samp_freq * .03)
    X = librosa.stft(
        np.array(speech_samples_norm[strt_samp:end_samp]), win_length=winlen)
    Xdb = librosa.amplitude_to_db(abs(X))

    plt.switch_backend('AGG')
    fg2 = plt.figure(figsize=(10, 4))
    librosa.display.specshow(Xdb, sr=samp_freq, x_axis='time',
                             y_axis='hz', hop_length=winlen / 4)

    flike = io.BytesIO()
    fg2.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    return b64

def short_term_energy(sig, winlen, fs):
    """ Gives the Short Term Energy  of the Audio"""
    winsamp = int(winlen*fs)
    stesig = np.zeros((len(sig)))
    for ind in range(int(winsamp/2), int(len(sig)-winsamp/2)):
        sig_segment = sig[int(ind-winsamp/2):int(ind+winsamp/2)]
        stesig[ind] = np.sum(np.multiply(sig_segment, sig_segment))

    return stesig


def silence(path):
    """ Gives the Silence - Amplitude Time Graph of the Audio"""
    #Reading the audio
    sound = AudioSegment.from_wav(path)
    sound_samples = sound.get_array_of_samples()
    samp_freq = sound.frame_rate

    speech_samples_norm = np.array(sound_samples) / np.max(np.array(sound_samples))

    #Calculating ShortTerm Energy for the audio
    winlen = .02  # Window length of 20 ms
    stesig = short_term_energy(speech_samples_norm, winlen, samp_freq)
    avgsig = np.mean(stesig)

    #Checking the area where energy is less than 0.1% of Average Enery
    silen = [i for i, v in enumerate(stesig) if v < avgsig * 10 ** (-4)]
    silen = np.array(silen)
    strt_samp = 0
    end_samp = len(speech_samples_norm)
    end_ms = len(speech_samples_norm) / samp_freq

    xrange = np.linspace(0, end_ms, end_samp - strt_samp)

    plt.switch_backend('AGG')
    fg1 = plt.figure(figsize=(10, 4))

    plt.plot(xrange, speech_samples_norm)

    plt.xlabel('Time in seconds')
    plt.ylabel('Amplitude')
    plt.axis('tight')
    plt.grid()

    # Silence regions
    silen_val = np.ones((len(silen))) * 0.5
    plt.plot(silen / samp_freq, silen_val, 'r*')
    plt.legend(['Speech signal', 'Silence segments'])

    flike = io.BytesIO()
    fg1.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    return b64


def emotionOutput(path):
    """ Using the Audio Analyser model to predict the Emotions"""
    X, sample_rate = librosa.load(path, res_type='kaiser_fast', duration=3, sr=22050 * 2)
    sample_rate = np.array(sample_rate)
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
    feature = mfccs
    df2 = feature
    df2 = pd.DataFrame(data=df2)
    df2 = df2.stack().to_frame().T
    df2expanded = np.expand_dims(df2, axis=2)
    loaded_model = load_model("AudioAnalyser.h5",custom_objects={'GlorotUniform': glorot_uniform()})
    pred = loaded_model.predict(df2expanded,batch_size=16,verbose=1)
    pred = pred.argmax(axis=1)
    predflatten = pred.astype(int).flatten()
    encoder = LabelEncoder()
    encoder.classes_ = np.load('encoder.npy',allow_pickle=True)
    livepredictions = (encoder.inverse_transform((predflatten)))
    return livepredictions[0]
