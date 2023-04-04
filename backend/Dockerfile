FROM python:3.9-slim-buster

RUN apt-get update && apt-get install gcc libcurl4-openssl-dev libssl-dev -y
RUN pip install --upgrade pip
RUN mkdir /backend
WORKDIR /backend
ADD requirements.txt /backend/
RUN pip install -r requirements.txt
ADD . /backend/

ARG CI
ARG APP_ENV
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
RUN export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
RUN if [ $CI ]; then python manage.py migrate --check --settings=config.settings.local; fi
RUN if [ $APP_ENV = dev ]; then python manage.py test --settings=config.settings.$APP_ENV api; fi
