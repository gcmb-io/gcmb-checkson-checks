FROM python:3.13-slim

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
