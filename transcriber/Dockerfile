FROM python:3.10-slim
RUN apt-get update && apt-get install -y libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "app:app"]
