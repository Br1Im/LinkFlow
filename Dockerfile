# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для Chrome и Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Google Chrome
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome.deb \
    && rm /tmp/google-chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем ChromeDriver
RUN wget -q https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json -O /tmp/versions.json \
    && CHROMEDRIVER_URL=$(python3 -c "import json; data=json.load(open('/tmp/versions.json')); print(data['channels']['Stable']['downloads']['chromedriver'][0]['url'])") \
    && wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 /tmp/versions.json

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY src/ ./src/
COPY tests/ ./tests/
COPY requirements.txt .

# Создаем директорию для скриншотов
RUN mkdir -p /app/screenshots

# Устанавливаем переменные окружения
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Запускаем Xvfb (виртуальный дисплей) и тесты
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python -m tests.test_multitransfer"]
