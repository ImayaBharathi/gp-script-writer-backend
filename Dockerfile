FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set Portry ENV 
ENV PATH="/root/.local/bin:$PATH"

# Create and set the working directory
WORKDIR /app

# Copy only the dependencies files to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN poetry install --no-root --no-dev

# Set the environment variable for the database URL
ARG DATABASE_URL=postgresql+psycopg2://postgres:admin@localhost/gp_dev_db
ENV SQLALCHEMY_DATABASE_URL=$DATABASE_URL


# Copy the entire application code into the container
COPY . /app/

# Expose the port your app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t gpbackenddev.azurecr.io/gp-backend-dev:latest .
# az container create --resource-group gp --name mycontainer --image mcr.microsoft.com/azuredocs/aci-helloworld --dns-name-label aci-demo --ports 80

# az container create --resource-group gp --name gp-backend-container --image gpbackenddev.azurecr.io/gp-backend-dev:latest --dns-name-label gp-backend --ports 8000
