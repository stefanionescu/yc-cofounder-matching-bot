FROM --platform=linux/amd64 selenium/standalone-chrome:125.0

# Set the working directory
WORKDIR /yc-cofounder-matching-bot

# Copy the current directory contents into the container
COPY . /yc-cofounder-matching-bot/

# Install Python and Pip
USER root
RUN apt-get update && apt-get install -y python-pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Command to run on container start
CMD ["python", "get_cofounder.py"]