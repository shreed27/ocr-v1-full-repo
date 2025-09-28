FROM python:2.7

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    mysql-client \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip setuptools
RUN pip install Django==1.4.22
RUN pip install MySQL-python==1.2.5
RUN pip install django-nose==1.4.7
RUN pip install South==1.0.2
RUN pip install coverage==4.5.4
RUN pip install django-extensions==1.9.9
RUN pip install requests==2.18.4
RUN pip install Pillow==5.4.1
RUN pip install nltk==2.0.4
RUN pip install numpy==1.16.6

# Create SQLite database directory
RUN mkdir -p /app/db

# Expose port
EXPOSE 8000

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=settings_local
ENV PYTHONPATH=/app:/app/algo

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
