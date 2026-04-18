FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    alsa-utils \
    gcc \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY voice_assistant.py .

CMD ["python", "voice_assistant.py"]
