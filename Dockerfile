FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Установка Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/google-chrome.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome.deb \
    && rm /tmp/google-chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# Установка ChromeDriver
RUN wget -q https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json -O /tmp/versions.json \
    && CHROMEDRIVER_URL=$(python3 -c "import json; data=json.load(open('/tmp/versions.json')); print(data['channels']['Stable']['downloads']['chromedriver'][0]['url'])") \
    && wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 /tmp/versions.json

WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY src/ ./src/
COPY admin/ ./admin/

# Создание директории для скриншотов
RUN mkdir -p /app/screenshots

EXPOSE 5001

CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python admin/api.py"]
