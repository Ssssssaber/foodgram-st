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
python manage.py import_ingredients ingredients.json --settings=foodgram.settings.deploy && \ 
gunicorn foodgram.wsgi:application --bind 0:8000 -c foodgram/settings/deploy.py"]
