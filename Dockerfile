# FROM python:3.10.13-slim
# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./test_entrypoint.sh /app/test_entrypoint.sh
# Copy the current directory contents into the container at /app
COPY ./src /app
# COPY ./frontend /app
COPY ./testing /app
#COPY ./testing/tests.sh /app/tests.sh

# Make the shell script executable
RUN chmod +x /app/entrypoint.sh

RUN chmod +x /app/test_entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt


EXPOSE $PORT

