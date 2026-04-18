import asyncio
import pyaudio
import numpy as np
import os
import time
import wave
import struct
import sys
sys.stdout.reconfigure(line_buffering=True)
from wyoming.asr import Transcribe
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import async_read_event, async_write_event
from wyoming.wake import Detection
from wyoming.event import async_read_event, async_write_event

# ─────────────────────────────────────────────
# CONFIG — edit these when your hardware arrives
# ─────────────────────────────────────────────
VOSK_IP = "127.0.0.1"
VOSK_PORT = 10300
WAKE_IP = "127.0.0.1"
WAKE_PORT = 10400

SAMPLE_RATE = 16000
CHANNELS = 1
WIDTH = 2           # 16-bit
CHUNK_BYTES = 3200  # 100ms of audio per read

# Set this to your USB mic's device index.
# Run `python -c "import pyaudio; p=pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"`
# to list devices and find your USB mic.
MIC_DEVICE_INDEX = 2  # None = system default

# Silence detection — stops recording after this many seconds of quiet
SILENCE_TIMEOUT = 2.0
SILENCE_THRESHOLD = 500  # RMS amplitude below this = silence

# How many seconds max to record a command before giving up
MAX_COMMAND_SECONDS = 15

# Path to your beep/confirmation sound (any WAV file)
# Generate a simple beep: `python -c "
#   import wave, struct, math
#   w=wave.open('beep.wav','w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
#   w.writeframes(struct.pack('<' + 'h'*1600, *[int(32767*math.sin(2*math.pi*880*i/16000)) for i in range(1600)]))
#   w.close()"`
BEEP_FILE = "beep.wav"

# ─────────────────────────────────────────────
# BEEP GENERATION (auto-creates beep.wav if missing)
# ─────────────────────────────────────────────
def ensure_beep():
    if not os.path.exists(BEEP_FILE):
        print("⚙ Generating beep.wav...")
        import math
        with wave.open(BEEP_FILE, 'w') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            samples = [
                int(32767 * math.sin(2 * math.pi * 880 * i / 16000))
                for i in range(3200)  # 200ms beep at 880Hz
            ]
            w.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
        print("✓ beep.wav created")


def play_beep():
    """Play beep.wav through the default audio output."""
    try:
        with wave.open(BEEP_FILE, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
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


# ─────────────────────────────────────────────
# WAKE WORD DETECTION
# ─────────────────────────────────────────────
async def wait_for_wake_word(mic_stream, loop):
    """
    Stream mic audio to OpenWakeWord continuously.
    Returns when the wake word is detected.
    """
    print("👂 Listening for wake word...")

    while True:
        try:
            reader, writer = await asyncio.open_connection(WAKE_IP, WAKE_PORT)
        except Exception as e:
            print(f"[Wake Error] Can't connect to OpenWakeWord: {e}")
            await asyncio.sleep(3)
            continue

        try:
            await async_write_event(
                AudioStart(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS).event(),
                writer
            )

            async def send_mic_to_wake():
                while True:
                    chunk = await loop.run_in_executor(
                        None, mic_stream.read, CHUNK_BYTES // WIDTH, False
                    )
                    await async_write_event(
                        AudioChunk(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS, audio=chunk).event(),
                        writer
                    )

            async def wait_for_detection():
                while True:
                    event = await async_read_event(reader)
                    if event is None:
                        return False
                    if event.type == "detection":
                        name = event.data.get("name", "unknown")
                        print(f"\n🎯 Wake word detected: '{name}'")
                        return True

            # Race: keep sending mic audio until wake word fires
            send_task = asyncio.create_task(send_mic_to_wake())
            detected = await wait_for_detection()
            send_task.cancel()

            if detected:
                return

        except Exception as e:
            print(f"[Wake Error]: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


# ─────────────────────────────────────────────
# COMMAND RECORDING
# ─────────────────────────────────────────────
async def record_command(mic_stream, loop) -> bytes:
    """
    Record audio from mic until silence or max duration.
    Returns raw PCM bytes.
    """
    print("🎤 Recording command...")
    audio_buffer = b""
    silence_start = None
    start_time = time.time()

    while True:
        chunk = await loop.run_in_executor(
            None, mic_stream.read, CHUNK_BYTES // WIDTH, False
        )
        audio_buffer += chunk

        # RMS silence detection
        samples = struct.unpack('<' + 'h' * (len(chunk) // 2), chunk)
        rms = int(np.sqrt(np.mean(np.array(samples, dtype=np.float32) ** 2)))

        if rms < SILENCE_THRESHOLD:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start >= SILENCE_TIMEOUT:
                print(f"🔇 Silence detected, stopped recording.")
                break
        else:
            silence_start = None  # Reset on speech

        if time.time() - start_time >= MAX_COMMAND_SECONDS:
            print("⏱ Max recording time reached.")
            break

    return audio_buffer


# ─────────────────────────────────────────────
# VOSK TRANSCRIPTION
# ─────────────────────────────────────────────
async def transcribe_audio(audio_bytes: bytes) -> str:
    """Send audio to Vosk, return transcript string."""
    try:
        reader, writer = await asyncio.open_connection(VOSK_IP, VOSK_PORT)
    except Exception as e:
        print(f"[Vosk Error] Connection failed: {e}")
        return ""

    try:
        await async_write_event(Transcribe().event(), writer)
        await async_write_event(
            AudioStart(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS).event(),
            writer
        )

        for i in range(0, len(audio_bytes), CHUNK_BYTES):
            piece = audio_bytes[i:i + CHUNK_BYTES]
            await async_write_event(
                AudioChunk(rate=SAMPLE_RATE, width=WIDTH, channels=CHANNELS, audio=piece).event(),
                writer
            )

        await async_write_event(AudioStop().event(), writer)

        while True:
            event = await asyncio.wait_for(async_read_event(reader), timeout=15.0)
            if event is None:
                break
            if event.type == "transcript":
                return event.data.get("text", "").strip()

    except asyncio.TimeoutError:
        print("[Vosk Error] Timed out waiting for transcript")
    except Exception as e:
        print(f"[Vosk Error]: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

    return ""


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
async def main():
    ensure_beep()

    loop = asyncio.get_event_loop()
    p = pyaudio.PyAudio()

    mic_stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=CHUNK_BYTES // WIDTH
    )

    print("✓ Microphone open")
    print("✓ Voice assistant ready\n")

    try:
        while True:
            # 1. Wait for wake word
            await wait_for_wake_word(mic_stream, loop)

            # 2. Play confirmation beep
            await loop.run_in_executor(None, play_beep)

            # 3. Record the command
            audio = await record_command(mic_stream, loop)

            # 4. Transcribe with Vosk
            print("⚙ Transcribing...")
            transcript = await transcribe_audio(audio)

            if transcript:
                print(f"\n📝 Command: \"{transcript}\"")
                # ─────────────────────────────────────────
                # TODO: pass `transcript` to your LLM agent
                # e.g. response = await my_llm_agent(transcript)
                # ─────────────────────────────────────────
            else:
                print("⚠️  Couldn't transcribe command.")

            print()  # blank line before next listen cycle

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down.")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()


if __name__ == "__main__":
    asyncio.run(main())
