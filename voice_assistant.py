import asyncio
import sys
sys.stdout.reconfigure(line_buffering=True)

from config import (
    DEBUG_SKIP_WAKE_WORD, DEBUG_SKIP_RECORDING,
    DEBUG_SKIP_LLM, DEBUG_SKIP_TTS,
    DEBUG_FAKE_TRANSCRIPT, DEBUG_FAKE_RESPONSE,
    LLM_PROVIDER, LLM_MODEL
)
from audio import open_mic
from wake import wait_for_wake_word
from transcribe import record_command, transcribe_audio
from llm import query_llm
from tts import speak


async def main():
    loop = asyncio.get_event_loop()
    p, mic_stream = open_mic()

    if mic_stream is None and not (DEBUG_SKIP_WAKE_WORD and DEBUG_SKIP_RECORDING):
        print("✗ No mic available and recording not skipped. Set DEBUG_SKIP_WAKE_WORD=True and DEBUG_SKIP_RECORDING=True in config.py")
        exit(1)

    print("✓ Microphone open")
    print("✓ Voice assistant ready")
    if any([DEBUG_SKIP_WAKE_WORD, DEBUG_SKIP_RECORDING, DEBUG_SKIP_LLM, DEBUG_SKIP_TTS]):
        print("⚠️  DEBUG MODE ACTIVE:")
        if DEBUG_SKIP_WAKE_WORD: print("   • Skipping wake word detection")
        if DEBUG_SKIP_RECORDING: print(f"   • Skipping recording — using: \"{DEBUG_FAKE_TRANSCRIPT}\"")
        if DEBUG_SKIP_LLM:       print(f"   • Skipping LLM — using: \"{DEBUG_FAKE_RESPONSE}\"")
        if DEBUG_SKIP_TTS:       print("   • Skipping TTS — printing response only")
    print()

    try:
        while True:
            # 1. Wake word
            if DEBUG_SKIP_WAKE_WORD:
                print("⚡ [DEBUG] Skipping wake word")
            else:
                await wait_for_wake_word(mic_stream, loop)

            # 2. Beep
            # 2. Confirmation — speak instead of beep
            await speak("Yes, I'm listening.")

            # 3. Record
            if DEBUG_SKIP_RECORDING:
                print(f"⚡ [DEBUG] Using fake transcript: \"{DEBUG_FAKE_TRANSCRIPT}\"")
                transcript = DEBUG_FAKE_TRANSCRIPT
            else:
                audio = await record_command(mic_stream, loop)
                print("⚙ Transcribing...")
                transcript = await transcribe_audio(audio)

            if not transcript:
                print("⚠️  Couldn't transcribe command.")
                await speak("Sorry, I didn't catch that. Please try again.")
                continue

            print(f"\n📝 Command: \"{transcript}\"")

            # 4. LLM
            if DEBUG_SKIP_LLM:
                print(f"⚡ [DEBUG] Using fake response: \"{DEBUG_FAKE_RESPONSE}\"")
                response = DEBUG_FAKE_RESPONSE
            else:
                print(f"⚙ Querying {LLM_PROVIDER} ({LLM_MODEL})...")
                response = await loop.run_in_executor(None, query_llm, transcript)
                print(f"🤖 Response: \"{response[:100]}{'...' if len(response) > 100 else ''}\"")

            # 5. TTS
            if DEBUG_SKIP_TTS:
                print(f"⚡ [DEBUG] TTS skipped. Full response:\n{response}")
            else:
                await speak(response)

            print()

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down.")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()


if __name__ == "__main__":
    asyncio.run(main())