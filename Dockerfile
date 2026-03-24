FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости (в которых уже должен быть flask)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем папки для данных
RUN mkdir -p data audio_cache logs

# --- ДОБАВЛЯЕМ ЭТУ СТРОКУ ---
# Это подсказка для Render, какой порт открыт в контейнере
EXPOSE 10000

# Запускаем основной файл (убедись, что это main.py или bot.py)
CMD ["python", "bot.py"] 
