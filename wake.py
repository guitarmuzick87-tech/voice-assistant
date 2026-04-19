import asyncio
from wyoming.audio import AudioStart, AudioChunk
from wyoming.event import async_read_event, async_write_event
from wyoming.wake import Detect
from audio import to_mono_16k
from config import WAKE_IP, WAKE_PORT, WAKE_WORD, SAMPLE_RATE, MIC_CHANNELS, WIDTH, CHUNK_BYTES


async def wait_for_wake_word(mic_stream, loop):
    print("👂 Listening for wake word...")

    while True:
        try:
            reader, writer = await asyncio.open_connection(WAKE_IP, WAKE_PORT)
        except Exception as e:
            print(f"[Wake Error] Can't connect to OpenWakeWord: {e}")
            await asyncio.sleep(3)
            continue

        try:
            await async_write_event(Detect(names=[WAKE_WORD]).event(), writer)
            await async_write_event(
                AudioStart(rate=16000, width=WIDTH, channels=1).event(), writer
            )

            async def send_mic():
                while True:
                    chunk = await loop.run_in_executor(
                        None, mic_stream.read, CHUNK_BYTES // WIDTH, False
                    )
                    chunk = to_mono_16k(chunk, src_rate=SAMPLE_RATE, src_channels=MIC_CHANNELS)
                    await async_write_event(
                        AudioChunk(rate=16000, width=WIDTH, channels=1, audio=chunk).event(),
                        writer
                    )

            async def wait_detection():
                while True:
                    event = await async_read_event(reader)
                    if event is None:
                        return False
                    if event.type == "detection":
                        print(f"\n🎯 Wake word detected: '{event.data.get('name')}'")
                        return True

            send_task = asyncio.create_task(send_mic())
            detected = await wait_detection()
            send_task.cancel()

            if detected:
                return

        except Exception as e:
            print(f"[Wake Error]: {e}")
        finally:
            writer.close()
            await writer.wait_closed()