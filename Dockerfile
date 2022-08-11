FROM python:3-buster
COPY requirements.txt scraper.py /app/
WORKDIR /app

RUN apt-get update
RUN apt-get install -y wget ffmpeg

RUN pip3 install -r requirements.txt
RUN pip3 install youtube-dl
ENTRYPOINT [ "python3", "scraper.py" ]
