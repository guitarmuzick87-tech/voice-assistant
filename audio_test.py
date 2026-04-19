import asyncio
import pyaudio

WAKE_IP = "127.0.0.1"
WAKE_PORT = 10400
MIC_DEVICE_INDEX = 1
SAMPLE_RATE = 16000
CHANNELS = 1
WIDTH = 2
CHUNK_BYTES = 3200

from wyoming.audio import AudioStart, AudioChunk
from wyoming.event import async_read_event, async_write_event
from wyoming.wake import Detect

async def test():
    loop = asyncio.get_event_loop()
    p = pyaudio.PyAudio()

    print("Opening mic...")
    mic_stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=CHUNK_BYTES // WIDTH
    )
    print("Mic open. Connecting to OpenWakeWord...")

    reader, writer = await asyncio.open_connection(WAKE_IP, WAKE_PORT)
    print("Connected. Sending AudioStart...")
    print("Connected. Sending Detect + AudioStart...")
    await async_write_event(Detect().event(), writer)  # ← add this

    await async_write_event(
        AudioStart(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS).event(),
        writer
    )
    print("Streaming audio chunks — speak the wake word now...")

    chunk_count = 0
    async def send():
        nonlocal chunk_count
        while True:
            chunk = await loop.run_in_executor(None, mic_stream.read, CHUNK_BYTES // WIDTH, False)
            await async_write_event(
                AudioChunk(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS, audio=chunk).event(),
                writer
            )
            chunk_count += 1
            if chunk_count % 10 == 0:
                print(f"  Sent {chunk_count} chunks...")

    async def receive():
        while True:
            event = await async_read_event(reader)
            if event is None:
                print("Connection closed by OpenWakeWord")
                break
            print(f"EVENT RECEIVED: type={event.type!r} data={event.data!r}")

    await asyncio.gather(send(), receive())

asyncio.run(test())
