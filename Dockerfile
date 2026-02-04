FROM python:3.11-slim

# Установка системных зависимостей для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements
COPY admin/requirements.txt /app/admin/requirements.txt
COPY requirements_playwright.txt /app/requirements_playwright.txt

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r /app/admin/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements_playwright.txt

# Устанавливаем Playwright браузеры
RUN playwright install chromium
RUN playwright install-deps chromium

# Копируем весь проект
COPY . /app/

# Создаем директорию для скриншотов
RUN mkdir -p /app/screenshots

# Инициализируем БД и импортируем данные из Excel
RUN python admin/database.py && \
    python import_excel_to_db.py || echo "Excel import skipped"

# Открываем порты
EXPOSE 5000 5001

# Запуск
CMD ["python", "start_admin.py"]
