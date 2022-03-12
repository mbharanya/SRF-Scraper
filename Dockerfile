FROM python:3-buster
COPY requirements.txt scraper.py /app/
WORKDIR /app

RUN apt-get update
RUN apt-get install -y wget

RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3", "scraper.py" ]