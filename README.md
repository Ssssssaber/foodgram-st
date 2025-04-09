# О проекте

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Зависимости

* Django Rest Framework - организация REST API
* Gunicorn - запуск веб-приложения
* Djoser - работа с учетными записями пользователей
* Postgres - база данных (sqlite при локальном развертывании)
* Nginx - прокси-сервер
* Docker - контейнеризация

# Запуск

## Docker

* Склонировать репозиторий
```bash
git clone https://github.com/Ssssssaber/foodgram-st
```
* В директории backend/foodgram/ создать .env файл с данными для подключения к базе данных. 
```bash
cd foodgram-st/backend/
touch .env
```
Пример файла, данные которого совпадают с данными в docker-compose.yml:
```env
export DB_NAME = foodgram
export DB_USER = foodgram_admin
export DB_USER_PASSWORD = kekeispassword
export DB_HOST = postgres
export DB_DB_PORT = 5432
```
* Перейти в директорию в infra/ и запустить команду
```bash
cd ../infra/
docker compose up
```
* Фикстуры при запуске docker compose загружаются автоматически
```Dockerfile
# foodgram-st/backend/Dockerfile
FROM python:3.12.3
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["bash", "-c", "python manage.py collectstatic --settings=foodgram.settings.deploy --noinput && \
python manage.py makemigrations --settings=foodgram.settings.deploy && \
python manage.py migrate --settings=foodgram.settings.deploy && \
python manage.py loaddata example_data/recipes.json --settings=foodgram.settings.deploy && \ 
gunicorn foodgram.wsgi:application --bind 0:8000 -c foodgram/settings/deploy.py"]
```

* Для тестирования админ-панели также нужно создать суперпользователя
```
docker exec backend python manage.py createsuperuser --settings=foodgram.settings.deploy
```
## Локальное развертывание без Docker

* Склонировать репозиторий
```
git clone https://github.com/Ssssssaber/foodgram-st
cd foodgram-st/backend/
```

* Создать виртуальную среду и активировать ее

```bash
# Windows
python -m venv venv
./venv/Scripts/activate
```

```bash
# Linux
python3 -m venv venv
source ./venv/bin/activate
```

* Установить зависимости из файла requirements.txt

```bash
pip install -r requirements.txt
```

* Выполнить миграции

```bash
# foodgram-st/backend
python manage.py migrate --settings=foodgram.settings.dev
```

* Создать суперпользователя 

```bash
python manage.py createsuperuser --settings=foodgram.settings.dev
```
* Заполнить базу данных ингридиентами

```bash
python manage.py import_ingredients ingredients.json --settings=foodgram.settings.dev
```

* Запустить сервер

```bash
python manage.py runserver --settings=foodgram.settings.dev
```

# API

* [Админ панель](http://127.0.0.1:8000/admin/); 
* [Корень API](http://127.0.0.1:8000/api/);
* [Документация к API](http://127.0.0.1/api/docs/);
* [Главная страница](http://127.0.0.1).

# Автор проекта

Лобанов Владимир Викторович
Telegram: @VVLobanov
Email (TPU): vvl45@gmail.com