# Dockerfile для админ-панели платежей
FROM python:3.9-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    xvfb \
    procps \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Установка Chrome и Chromedriver
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Установка Chromedriver (автоматически подбирается версия)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && echo "Chrome version: $CHROME_VERSION" \
    && wget -q "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}" -O /tmp/version.txt \
    && DRIVER_VERSION=$(cat /tmp/version.txt) \
    && echo "Driver version: $DRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/bin/ \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf /tmp/chromedriver* /tmp/version.txt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/

RUN mkdir -p /app/bot/temp_qr /app/bot/profiles /app/bot/chrome_profile

# НЕ создаем отдельного пользователя - запускаем от root для упрощения
# RUN useradd -m chrome && chown -R chrome:chrome /app
# USER chrome

# Настройки для Chrome в Docker
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Запускаем Xvfb и приложение
CMD ["sh", "-c", "pkill Xvfb 2>/dev/null || true && rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1920x1080x24 & sleep 2 && cd bot && python admin_panel.py"]