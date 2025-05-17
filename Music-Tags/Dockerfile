FROM python:3.10-slim-bullseye

WORKDIR /app

COPY ./requirements.txt /app/
COPY ./run.py /app/

RUN pip install --no-cache-dir --upgrade setuptools pip
RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["python", "run.py"]
