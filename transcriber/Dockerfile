FROM python:3.10-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py ./

# Verify files are copied
RUN ls -la

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]