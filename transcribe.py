import asyncio
from wyoming.asr import Transcribe
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import async_read_event, async_write_event
from config import VOSK_IP, VOSK_PORT, WIDTH, CHUNK_BYTES
import time
import struct
import numpy as np
from audio import to_mono_16k
from config import SAMPLE_RATE, MIC_CHANNELS, SILENCE_THRESHOLD, SILENCE_TIMEOUT, MAX_COMMAND_SECONDS


async def record_command(mic_stream, loop) -> bytes:
    print("🎤 Recording command...")
    audio_buffer = b""
    silence_start = None
    start_time = time.time()

    while True:
        chunk = await loop.run_in_executor(
            None, mic_stream.read, CHUNK_BYTES // WIDTH, False
        )
        converted = to_mono_16k(chunk, src_rate=SAMPLE_RATE, src_channels=MIC_CHANNELS)
        audio_buffer += converted

        samples = struct.unpack('<' + 'h' * (len(converted) // 2), converted)
        rms = int(np.sqrt(np.mean(np.array(samples, dtype=np.float32) ** 2)))

        if rms < SILENCE_THRESHOLD:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start >= SILENCE_TIMEOUT:
                print("🔇 Silence detected, stopped recording.")
                break
        else:
            silence_start = None

        if time.time() - start_time >= MAX_COMMAND_SECONDS:
            print("⏱ Max recording time reached.")
            break

    return audio_buffer


async def transcribe_audio(audio_bytes: bytes) -> str:
    try:
        reader, writer = await asyncio.open_connection(VOSK_IP, VOSK_PORT)
    except Exception as e:
        print(f"[Vosk Error] Connection failed: {e}")
        return ""

    try:
        await async_write_event(Transcribe().event(), writer)
        await async_write_event(
            AudioStart(rate=16000, width=WIDTH, channels=1).event(), writer
        )
        for i in range(0, len(audio_bytes), CHUNK_BYTES):
            await async_write_event(
                AudioChunk(rate=16000, width=WIDTH, channels=1,
                           audio=audio_bytes[i:i + CHUNK_BYTES]).event(), writer
            )
        await async_write_event(AudioStop().event(), writer)

        while True:
            event = await asyncio.wait_for(async_read_event(reader), timeout=15.0)
            if event is None:
                break
            if event.type == "transcript":
                return event.data.get("text", "").strip()

    except asyncio.TimeoutError:
        print("[Vosk Error] Timed out")
    except Exception as e:
        print(f"[Vosk Error]: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

    return ""