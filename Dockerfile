FROM python:3.13-slim
LABEL maintainer="yakovenkoanton2007@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /files/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /files/media
RUN chmod 755 /files/media

USER my_user

CMD python manage.py wait_for_db && python manage.py migrate && gunicorn airport_api_service.wsgi:application --bind 0.0.0.0:${PORT:-8000}