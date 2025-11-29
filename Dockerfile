FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/qrcodes

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
