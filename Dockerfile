FROM python:3.10.13-slim

LABEL Blockchat Blockchain

# Environment Variables
ENV IP                   192.168.1.10
ENV PORT                 6789
ENV BOOTSTRAP            True
ENV IP_BOOTSTRAP	 	 192.168.1.10
ENV PORT_BOOTSTRAP	 	 6789
ENV NODES		 		 5
ENV CAPACITY		 	 2


# Copy files
COPY ./requirements.txt /app/requirements.txt
COPY . /app

# Set working directory
WORKDIR /app

# Debian/Ubuntu commands:
RUN apt-get update && apt-get install gcc -y && \
pip install -r requirements.txt

