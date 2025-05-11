FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "2", "--bind", "0.0.0.0:5005", "app:app"]

