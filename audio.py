import audioop
import math
import numpy as np
import pyaudio
import struct
import wave
from config import (
    BEEP_FILE, CHUNK_BYTES, WIDTH, SAMPLE_RATE,
    MIC_CHANNELS, SPEAKER_DEVICE_INDEX, MIC_DEVICE_INDEX, SPEAKER_CHANNELS, SPEAKER_RATE
)


def to_mono_16k(data, src_rate=44100, src_channels=1):
    if src_channels == 2:
        data = audioop.tomono(data, 2, 0.5, 0.5)
    data, _ = audioop.ratecv(data, 2, 1, src_rate, 16000, None)
    return data


def ensure_beep():
    import os
    if not os.path.exists(BEEP_FILE):
        print("⚙ Generating beep.wav...")
        with wave.open(BEEP_FILE, 'w') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            samples = [
                int(32767 * math.sin(2 * math.pi * 880 * i / 16000))
                for i in range(3200)
            ]
            w.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
        print("✓ beep.wav created")


def play_beep():
    try:
        with wave.open(BEEP_FILE, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),  # uses whatever the WAV file specifies
                rate=wf.getframerate(),
                output=True,
                output_device_index=SPEAKER_DEVICE_INDEX
            )
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            p.terminate()
    except Exception as e:
        print(f"[Beep Error]: {e}")


def play_audio_bytes(audio_bytes: bytes, rate: int = None, channels: int = None):
    rate = rate or SPEAKER_RATE
    channels = channels or SPEAKER_CHANNELS
    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=SPEAKER_DEVICE_INDEX
        )
        stream.write(audio_bytes)
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        print(f"[Playback Error]: {e}")


def open_mic():
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=MIC_CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=MIC_DEVICE_INDEX,
            frames_per_buffer=CHUNK_BYTES // WIDTH
        )
        return p, stream
    except Exception as e:
        print(f"⚠️  Could not open mic (device index {MIC_DEVICE_INDEX}): {e}")
        print("   Set DEBUG_SKIP_WAKE_WORD and DEBUG_SKIP_RECORDING in config.py to run without a mic.")
        return p, None