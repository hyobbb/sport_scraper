FROM python:3.9.4

RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED 1
WORKDIR /sport_scraper
COPY . .
RUN pip install -r requirements.txt
