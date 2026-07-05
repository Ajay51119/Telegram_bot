# Slim Python base — matches the version this project was built/tested against.
FROM python:3.12-slim

# Don't write .pyc files, and flush stdout/stderr immediately so `docker logs`
# shows bot activity in real time instead of buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for resume OCR: tesseract-ocr (text recognition engine) +
# poppler-utils (renders PDF pages to images for pdf2image to feed Tesseract).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install deps first so this layer is cached and only re-runs when
# requirements.txt actually changes (faster rebuilds while you iterate).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app.
COPY . .

# Run as a non-root user (good practice for a long-running network process).
RUN useradd --create-home --shell /bin/bash botuser \
    && chown -R botuser:botuser /app
USER botuser

# This is a polling bot (outbound HTTPS only to Telegram/Groq/OpenRouter) —
# no inbound port needs to be exposed.
CMD ["python", "bot.py"]
