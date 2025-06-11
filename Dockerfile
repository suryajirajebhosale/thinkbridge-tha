# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /code/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

# Set proper permissions
RUN chmod -R 755 /code
RUN echo "Working dir is: $(pwd)"
# Expose port for Jupyter notebook (optional)
EXPOSE 8888

# Expose port for web interface (if you add one later)
EXPOSE 8000

# Default command - can be overridden in docker-compose
CMD ["python", "-m", "src.researcher"]