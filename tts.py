import asyncio
from wyoming.tts import Synthesize
from wyoming.event import async_read_event, async_write_event
from audio import play_audio_bytes
from config import PIPER_IP, PIPER_PORT


async def speak(text: str):
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
                audio_buffer += event.payload
                
            elif event.type == "audio-stop":
                break



        writer.close()
        await writer.wait_closed()

        if audio_buffer:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, play_audio_bytes, audio_buffer, rate, channels)

    except asyncio.TimeoutError:
        print("[Piper Error] Timed out")
    except Exception as e:
        print(f"[Piper Error]: {e}")