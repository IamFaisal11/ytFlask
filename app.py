from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp
import os
import shutil

app = Flask(__name__)

# Default download folder (inside static directory)
DOWNLOAD_FOLDER = 'static/downloads'

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Check if ffmpeg is installed
def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

# Function to download the YouTube playlist
def download_playlist(playlist_url):
    if not is_ffmpeg_installed():
        return {"status": "error", "message": "ffmpeg is not installed or not found in PATH. Please install ffmpeg to proceed."}

    # Set options for yt-dlp
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',  # 1080p or lower
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save to default folder
        'noplaylist': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert to mp4
        }],
        'progress_hooks': [print_download_progress],  # Print download progress (optional)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        return {"status": "success", "message": "Playlist downloaded successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Function to print download progress
def print_download_progress(d):
    if d['status'] == 'finished':
        print(f"\nDone downloading {d['filename']}")

# Flask route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Flask route to handle playlist download
@app.route('/download', methods=['POST'])
def download():
    playlist_url = request.form['playlist_url']
    result = download_playlist(playlist_url)
    if result['status'] == 'success':
        # After downloading, get the list of downloaded files
        downloaded_files = os.listdir(DOWNLOAD_FOLDER)
        if downloaded_files:
            file_path = os.path.join(DOWNLOAD_FOLDER, downloaded_files[-1])  # Get the last downloaded file
            return send_file(file_path, as_attachment=True)  # Send file for download
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
