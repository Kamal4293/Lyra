# Use Python 3.10 to match your app requirements
FROM python:3.10

# 1. INSTALL CRITICAL NETWORK TOOLS
# 'ca-certificates' helps with secure connections
# 'dnsutils' and 'iputils-ping' fix the "No address" DNS errors
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

# 4. Copy App Code
COPY --chown=user . /app

# 5. Download Brain (Signatures)
RUN wget https://huggingface.co/datasets/Kamal429316/lyra-brain-data/resolve/main/signatures.zip -O signatures.zip

# 6. Unzip
RUN unzip signatures.zip && rm signatures.zip

# 7. Create Music Folder
RUN mkdir -p static/music

# 8. Start App
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "app:app"]
