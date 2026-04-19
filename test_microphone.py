import pyaudio
import time

MIC_DEVICE_INDEX = 1
SAMPLE_RATE = 16000
CHUNK = 1600

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE,
    input=True,
    input_device_index=MIC_DEVICE_INDEX,
    frames_per_buffer=CHUNK
)

print("Monitoring mic input — Ctrl+C to stop\n")
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = [
            abs(int.from_bytes(data[i:i+2], 'little', signed=True))
            for i in range(0, len(data), 2)
        ]
        rms = int((sum(s**2 for s in samples) / len(samples)) ** 0.5)
        bar = '█' * (rms // 100)
        print(f'\rRMS: {rms:5d} |{bar:<50}|', end='', flush=True)
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nDone.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
