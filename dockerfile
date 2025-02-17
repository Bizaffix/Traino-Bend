# Use official Python image as a base
FROM python:3.11


# Set environment variables to prevent prompts during package installation
ENV PYTHONUNBUFFERED=1

# Set work directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . .

# Expose the port that Django runs on
EXPOSE 8000

# Run the Django application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "traino_local.wsgi:application"]
