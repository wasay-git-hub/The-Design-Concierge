# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
# ReportLab and other packages sometimes need these libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.backend.api_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
