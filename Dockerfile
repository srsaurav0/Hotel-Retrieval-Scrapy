FROM python:3.9-slim

# Install system-level dependencies for PostgreSQL and Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Scrapy project and other necessary files
COPY . .

# Run the database initialization script before starting the Scrapy spider
CMD ["sh", "-c", "python initialize_db.py && scrapy crawl city_hotels && sleep infinity"]