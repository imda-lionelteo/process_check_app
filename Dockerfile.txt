# Use the official Python base image for building
FROM python:3.12-slim AS build

# Set the working directory
WORKDIR /app

# Copy the requirements file and README.md into the container
COPY pyproject.toml poetry.lock README.md ./

# Install the required packages
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-root

# Copy the rest of the application code into the container
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "streamlit_app.py"]
