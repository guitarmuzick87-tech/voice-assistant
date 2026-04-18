FROM python:3.11-slim

# System dependencies PyAudio needs to compile
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cached layer if requirements don't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY voice_assistant.py .

CMD ["python", "voice_assistant.py"]
