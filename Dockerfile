FROM --platform=linux/amd64 selenium/standalone-chrome:126.0

# Set the working directory
WORKDIR /yc-cofounder-matching-bot

# Copy the current directory contents into the container
COPY . /yc-cofounder-matching-bot/

# Install Python 3 and Pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Command to run on container start
CMD ["python3", "get_cofounder.py"]