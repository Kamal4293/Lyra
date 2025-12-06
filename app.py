from flask import Flask, request, render_template
import os
import yt_dlp
import subprocess
import sys
from urllib.parse import quote

app = Flask(__name__)

# Cloud paths need to be created explicitly sometimes
os.makedirs("static/music", exist_ok=True)

# Clean up any leftover audio files on startup (keeps storage low)
os.system('rm -rf static/music/*.mp3')
# Clean up metadata to prevent ghost names
if os.path.exists("static/music/original_meta.txt"):
    os.remove("static/music/original_meta.txt")
if os.path.exists("static/music/recommended.txt"):
    os.remove("static/music/recommended.txt")

def fetch_from_youtube(song_name):
    """Searches YouTube and downloads the song to 'cloud_playing.mp3'"""
    print(f"--> Fetching Stream: {song_name}")
    
    output_path = "static/music/cloud_playing"
    final_path = "static/music/cloud_playing.mp3"
    
    if os.path.exists(final_path):
        os.remove(final_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True,
        # 'cookies': 'cookies.txt', # Uncomment if you upload cookies.txt for better stability
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([song_name])
        return True
    except Exception as e:
        print(f"Stream Error: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    status = ""
    
    # Default State
    active_query = "static/music/query1.mp3"
    active_title = "Waiting for input..."
    
    original_query = "static/music/query1.mp3"
    original_title = "No analysis yet"
    
    # Load persistence if available
    if os.path.exists("static/music/original_meta.txt"):
        with open("static/music/original_meta.txt", "r") as f:
            original_title = f.read().strip()
            active_title = original_title

    recommendations = []

    if request.method == "POST":
        action = request.form.get("action", "analyze")

        # --- ANALYZE ---
        if action == "analyze":
            url = request.form.get("url")
            try:
                # Remove old files
                if os.path.exists(original_query): os.remove(original_query)
                
                ydl_opts = {
                    'format': 'bestaudio/best', 'outtmpl': "static/music/query1", 
                    'noplaylist': True,
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'Unknown Song')
                    
                    active_title = title
                    original_title = title
                    with open("static/music/original_meta.txt", "w") as f: f.write(title)

                # Run The Logic
                subprocess.run([sys.executable, "test5.py"], check=True)
                
                status = "✅ Analysis Complete"
            except Exception as e:
                status = f"❌ Error: {str(e)}"

        # --- FETCH STREAM ---
        elif action == "play_cloud":
            song_name = request.form.get("song_name")
            status = f"⏳ Streaming '{song_name}'..."
            
            if fetch_from_youtube(song_name):
                status = f"▶️ Playing: {song_name}"
                active_query = "static/music/cloud_playing.mp3"
                active_title = f"[Cloud] {song_name}"
            else:
                status = "❌ Stream Failed"

    # Load Recommendations
    if os.path.exists("static/music/recommended.txt"):
        with open("static/music/recommended.txt", "r") as f:
            for line in f.readlines():
                text = line.strip()
                if text:
                    # Check if it's just numbers (like "851")
                    # allow_fetch is False if it contains ONLY digits/dots
                    is_numeric = text.replace('.', '').replace(' ', '').isdigit()
                    recommendations.append({
                        "name": text,
                        "allow_fetch": not is_numeric
                    })

    return render_template("index.html", 
                         query=active_query, 
                         input_title=active_title,
                         original_query=original_query,
                         original_title=original_title,
                         recommendations=recommendations,
                         status=status)

if __name__ == "__main__":
    # Hugging Face usually provides PORT 7860
    app.run(debug=True, port=7860)