# voice-assistant
Voice assistant module for the mobile robot


# Requires python 3.13
# For MacOS you will need to install the following:

PortAudio

# brew install portaudio

You'll also need to configure the script by different device ID channels and numbers

# Run this to find your device ID and channels
python -c "
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    print(i, '|', d['name'], '| in:', d['maxInputChannels'], '| out:', d['maxOutputChannels'], '| rate:', int(d['defaultSampleRate']))
p.terminate()
"