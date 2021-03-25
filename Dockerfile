FROM python:3.7

WORKDIR /app

# Копирую сначала зависимости
# Для того чтобы не пересобирать их каждый раз при сборке
COPY requirements.txt .

# Выполняю необходимые команды
RUN pip install -U pip
RUN pip install -r requirements.txt

# Копирую остальные файлы проекта
COPY . .

# Выствляем порт наружу
EXPOSE 5000

# Запускаем приложение
ENTRYPOINT ["python", "app.py"]