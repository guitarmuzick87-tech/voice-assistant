import asyncio
import threading
from wyoming.tts import Synthesize
from wyoming.event import async_read_event, async_write_event
from audio import play_audio_bytes
from config import PIPER_IP, PIPER_PORT, INTERRUPT_ENABLED


class InterruptiblePlayer:
    """Plays audio in a thread that can be stopped mid-playback."""

    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None

    def play(self, audio_bytes: bytes, rate: int, channels: int):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._play_thread,
            args=(audio_bytes, rate, channels),
            daemon=True
        )
        self._thread.start()

    def _play_thread(self, audio_bytes: bytes, rate: int, channels: int):
        import pyaudio
        from config import SPEAKER_DEVICE_INDEX
        CHUNK = 1024 * 4

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=SPEAKER_DEVICE_INDEX
        )
        try:
            offset = 0
            while offset < len(audio_bytes):
                if self._stop_event.is_set():
                    print("🛑 Playback interrupted.")
                    break
                chunk = audio_bytes[offset:offset + CHUNK]
                stream.write(chunk)
                offset += CHUNK
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def is_playing(self):
        return self._thread is not None and self._thread.is_alive()


async def speak(text: str, mic_stream=None, loop=None) -> bool:
    """
    Speak text via Piper. If mic_stream provided, listens for interrupt word.
    Returns True if interrupted, False if completed normally.
    """
    print(f"🔊 Speaking: \"{text[:60]}{'...' if len(text) > 60 else ''}\"")
    try:
        reader, writer = await asyncio.open_connection(PIPER_IP, PIPER_PORT)
        await async_write_event(Synthesize(text=text).event(), writer)

        audio_buffer = b""
        rate, channels = 22050, 1

        while True:
            event = await asyncio.wait_for(async_read_event(reader), timeout=30.0)
            if event is None:
                break
            if event.type == "audio-start":
                rate = event.data.get("rate", 22050)
                channels = event.data.get("channels", 1)
            elif event.type == "audio-chunk":
                if event.payload:
                    audio_buffer += event.payload
            elif event.type == "audio-stop":
                break

        writer.close()
        await writer.wait_closed()

        if not audio_buffer:
            return False

        # Play audio with optional interrupt detection
        player = InterruptiblePlayer()
        player.play(audio_buffer, rate, channels)

        if INTERRUPT_ENABLED and mic_stream and loop:
            # Poll for interrupt word while audio plays
            while player.is_playing():
                interrupted = await listen_for_interrupt(mic_stream, loop)
                if interrupted:
                    player.stop()
                    return True  # signal that we were interrupted
        else:
            # No interrupt — just wait for playback to finish
            while player.is_playing():
                await asyncio.sleep(0.1)

        return False

    except asyncio.TimeoutError:
        print("[Piper Error] Timed out")
    except Exception as e:
        print(f"[Piper Error]: {e}")

    return False


async def listen_for_interrupt(mic_stream, loop) -> bool:
    from transcribe import transcribe_audio
    from audio import to_mono_16k
    from config import INTERRUPT_WORD, SAMPLE_RATE, MIC_CHANNELS, WIDTH, CHUNK_BYTES

    audio = b""
    for _ in range(10):
        chunk = await loop.run_in_executor(
            None, mic_stream.read, CHUNK_BYTES // WIDTH, False
        )
        audio += to_mono_16k(chunk, src_rate=SAMPLE_RATE, src_channels=MIC_CHANNELS)

    from transcribe import transcribe_audio
    transcript = await transcribe_audio(audio)
    if transcript:
        print(f"[Interrupt check] heard: '{transcript}'")
        return INTERRUPT_WORD.lower() in transcript.lower()
    return False