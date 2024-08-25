FROM python:3.10-bullseye

WORKDIR /app

COPY ./requirements.txt /app/
COPY ./run.py /app/

RUN apt update -y && apt upgrade -y
RUN apt install -y ffmpeg

RUN pip install --no-cache-dir --upgrade setuptools pip
RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["python", "run.py"]
