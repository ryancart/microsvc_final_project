FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003
CMD ["gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:8003", "app:app"]
