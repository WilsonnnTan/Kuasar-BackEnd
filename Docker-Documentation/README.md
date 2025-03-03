# Docker Documentation

## 1. Container Architecture

### Dockerfile Overview

The `Dockerfile` defines the steps needed to build a Docker image for your FastAPI application. It starts from a Python 3.9 slim image and sets up the necessary environment for the application to run.

- **Base Image**: `python:3.9-slim`  
  This image is a minimal version of Python 3.9, designed to keep the image size small while still supporting Python-based applications.

- **Working Directory**: `/my-app`  
  This is the directory inside the container where the application will reside.

- **Install Dependencies**:  
  The `requirements.txt` file is copied into the container, and then all dependencies listed inside are installed using `pip`.

- **Application Code**:  
  The rest of the application code is copied into the container. This allows your FastAPI application to be available inside the container.

- **Expose Port**:  
  Port `8000` is exposed, which is the default port for FastAPI to run.

- **CMD**:  
  The command to run the FastAPI application is set using `uvicorn`, which serves the FastAPI app. The `--reload` flag enables hot reloading during development.

### Docker Compose Overview

The `docker-compose.yml` file orchestrates the multi-container setup, defining services for the FastAPI application and the PostgreSQL database. It simplifies the process of managing multiple containers and their dependencies.

#### Services

1. **App (FastAPI Service)**:
   - **Build Configuration**:  
     The app is built from the current directory (with `Dockerfile` located in the `Docker/` folder).  
     The environment variables needed for the app to function are pulled from a `.env` file.

   - **Ports**:  
     Port 8000 is mapped from the container to the host, so you can access the FastAPI application from `localhost:8000`.

   - **Environment Variables**:  
     These variables, such as `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`, are defined in the `.env` file and used by the app for database connections and JWT token management.

   - **Depends On**:  
     The app service depends on the `db` service (PostgreSQL), ensuring that the database container starts before the FastAPI app.

2. **Database (PostgreSQL Service)**:
   - **Image**:  
     The official `postgres:13` image is used to run the PostgreSQL database.

   - **Environment Variables**:  
     The database credentials are configured via the `.env` file with `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.

   - **Volumes**:  
     A named volume `postgres_data` is used to persist the database data, ensuring that data is retained even if the container is stopped or recreated.

#### Volumes

- **postgres_data**:  
  This is a named volume that stores PostgreSQL data persistently, located at `/var/lib/postgresql/data` in the container. It ensures that the database persists across container restarts.

To view all Docker volumes, run:

```bash
docker volume ls
```

## 2. Volume Management

In Docker, volumes are used to persist data generated by and used by Docker containers. Volumes are the preferred mechanism for persisting data in Docker, as they provide a more efficient and flexible way of managing data compared to bind mounts.

This project uses Docker volumes for persistent data storage of the PostgreSQL database.

### Creating and Managing Volumes

In our `docker-compose.yml`, the `postgres_data` volume is defined for the database service. This ensures that the PostgreSQL container's data is stored persistently even if the container is stopped or removed.

Here’s the relevant portion of the `docker-compose.yml` that defines the volume:

```yaml
services:
  db:
    image: postgres:13
    container_name: postgres_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistent data storage

volumes:
  postgres_data:
    # Volume to store the database data
```


## 3. Docker Development and Production Configurations

### Development Configuration

In the development environment, the goal is to facilitate fast iteration while developing your application. Docker provides the following development configuration:

#### Dockerfile (Development Mode)
In the `Dockerfile`, we use the `--reload` flag with `uvicorn` to enable automatic reloading of the FastAPI application when changes are made to the source code.


```Dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /my-app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

```

#### docker-compose.yml (Development Mode)

The `docker-compose.yml` file is configured to work with PostgreSQL and FastAPI in a development environment. It will automatically reload the FastAPI application on changes and make the application available at `localhost:8000`.

```yaml
version: "3.8"

services:
  # Application service
  app:
    build:
      context: .  # Build from the current directory
      dockerfile: Dockerfile  # Dockerfile for FastAPI application
    container_name: fastapi_app
    ports:
      - "8000:8000"  # Expose FastAPI application on port 8000
    environment:
      - DATABASE_URL=${DATABASE_URL}  # Pull the DATABASE_URL from the .env file
      - SECRET_KEY=${SECRET_KEY}      # Pull the SECRET_KEY from the .env file
      - ALGORITHM=${ALGORITHM}        # Pull the ALGORITHM from the .env file
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}  # Pull the expiration time for access tokens
    depends_on:
      - db  # Ensure the database service starts before the app

  # Database service (PostgreSQL)
  db:
    image: postgres:13  # Use official PostgreSQL image
    container_name: postgres_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}         # Use POSTGRES_USER from the .env file
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD} # Use POSTGRES_PASSWORD from the .env file
      POSTGRES_DB: ${POSTGRES_DB}             # Use POSTGRES_DB from the .env file
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistent data storage

volumes:
  postgres_data:  # Create a named volume to persist database data
```

### Production Configuration

#### Dockerfile (Production Mode)

In the production environment, we remove the `--reload` flag to avoid unnecessary overhead. Additionally, it is recommended to use `gunicorn` for serving the FastAPI application for better performance in production.

```Dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /my-app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8000
EXPOSE 8000

# Install gunicorn for production use
RUN pip install gunicorn

# Command to run the FastAPI application using gunicorn (no --reload flag in production)
CMD ["gunicorn", "-w", "4", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```


#### docker-compose.yml (Production Mode)

The docker-compose.yml file remains mostly the same as Development Mode, but you may need to change some configuration based on the `production database` and `environment variables`.
