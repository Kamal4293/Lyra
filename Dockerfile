# Use Python 3.10
FROM python:3.10

# 1. Install System Tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    unzip \
    wget \
    ca-certificates \
    dnsutils \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup User
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /app

# 3. Install Python Libraries
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copy Code & Startup Script
COPY --chown=user . /app

# 5. Make the startup script executable
RUN chmod +x start.sh

# 6. Create Music Folder
RUN mkdir -p static/music

# 7. COMMAND: Run the startup script instead of gunicorn directly
CMD ["./start.sh"]
