FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
COPY src/ .

RUN pip install --no-cache-dir --upgrade setuptools pip
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "src/main.py"]
