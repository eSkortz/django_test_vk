# используем образ Python 3.8
FROM python:3.8

# создаем директорию приложения внутри контейнера
RUN mkdir /app

# устанавливаем рабочую директорию
WORKDIR /app

# копируем зависимости проекта и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# копируем все файлы проекта в контейнер
COPY . /app/

# запускаем команду для миграции базы данных
RUN python manage.py migrate

# запускаем приложение при старте контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
