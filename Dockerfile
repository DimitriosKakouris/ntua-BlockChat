# FROM python:3.10.13-slim
# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster


# LABEL Blockchat Blockchain

# # Environment Variables

# ENV BOOTSTRAP            True
# ENV IP_BOOTSTRAP	 	 172.18.0.2
# ENV PORT_BOOTSTRAP	 	 8000
# ENV NODES		 		 5
# ENV CAPACITY		 	 2


# # Copy files
# COPY ./requirements.txt /app/requirements.txt
# COPY . /app

# # Set working directory
# WORKDIR /app

# # Debian/Ubuntu commands:
# RUN apt-get update && apt-get install gcc -y && \
# pip install -r requirements.txt


# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
# Copy the current directory contents into the container at /app
COPY ./src /app


# Make the shell script executable
RUN chmod +x /app/entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE $PORT

# Use the shell script as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]