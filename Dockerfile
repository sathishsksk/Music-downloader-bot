FROM sathishsk/music

RUN apt-get -y update 
RUN apt-get install -y ffmpeg 

WORKDIR /app

copy requirements.txt req.txt

COPY . .

EXPOSE <8080>

CMD ["python3", "bot.py"]
