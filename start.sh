#!/bin/bash

# 1. Check if the brain is already there (to save time on restarts)
if [ ! -d "signatures" ]; then
    echo "🧠 Brain missing. Downloading from Locker..."
    
    # Download the 5GB file (The link you created earlier)
    wget https://huggingface.co/datasets/Kamal429316/lyra-brain-data/resolve/main/signatures.zip -O signatures.zip
    
    echo "📂 Unzipping the brain..."
    unzip signatures.zip
    
    # Clean up the zip file to save space
    rm signatures.zip
    
    echo "✅ Brain installation complete."
else
    echo "🧠 Brain already exists. Skipping download."
fi

# 2. Start the Music App
echo "🎵 Starting Lyra Engine..."
gunicorn -b 0.0.0.0:7860 --timeout 120 app:app
