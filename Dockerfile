# Dockerfile

# 1. Start with a suitable base image (Python 3.11 is a stable choice)
FROM python:3.11-slim

# 2. Install Deno (The recommended JavaScript runtime for yt-dlp)
# We download the latest Deno binary, unzip it, and add it to the system PATH.
ENV DENO_INSTALL "/usr/local"
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deno.land/install.sh | sh
ENV PATH "$DENO_INSTALL/bin:$PATH"

# 3. Set the working directory inside the container
WORKDIR /usr/src/app

# 4. Copy required files
COPY requirements.txt .
COPY . .

# 5. Install Python dependencies (Flask, Gunicorn, yt-dlp)
# yt-dlp is installed here, inheriting Deno from the PATH above.
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose the port Gunicorn will listen on
EXPOSE 10000

# 7. Define the startup command using Gunicorn
# Render requires services to listen on the port defined by the PORT environment variable.
CMD gunicorn app-web:app --bind 0.0.0.0:$PORT
