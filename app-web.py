# app.py (Final Version with URL Cleanup)
import os
import subprocess
import json
import uuid
import re
from flask import Flask, render_template, request, send_file
# NEW: Import for URL parsing
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode 

app = Flask(__name__)
# Define a temporary directory for downloads
DOWNLOAD_DIR = 'temp_downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    """Renders the main download page."""
    return render_template('app.html')

@app.route('/download', methods=['POST'])
def download():
    """Handles the media download request, cleaning the title and URL."""
    # 1. Get form data
    url = request.form.get('url')
    format_ext = request.form.get('fm')
    
    if not url or not format_ext:
        return "Error: Missing URL or format.", 400

    # --- NEW: URL CLEANING LOGIC ---
    # Parse the URL to identify and remove the 'list' (playlist) parameter
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Remove the 'list' parameter from the query if it exists
        if 'list' in query_params:
            del query_params['list']
        
        # Reconstruct the query string without the 'list' parameter
        cleaned_query = urlencode(query_params, doseq=True)

        # Reconstruct the final URL
        # We need to explicitly pass the path and network location back
        cleaned_url = urlunparse(parsed_url._replace(query=cleaned_query, fragment=''))
    except Exception:
        # Fallback to the original URL if parsing fails
        cleaned_url = url
    # --- END NEW URL CLEANING LOGIC ---
    
    # 2. Extract Metadata (Title) using the cleaned_url
    try:
        # Use the cleaned_url here to avoid playlist-related metadata errors
        meta_command = ['yt-dlp', '--dump-json', '--', cleaned_url]
        meta_process = subprocess.run(meta_command, check=True, capture_output=True, text=True)
        metadata = json.loads(meta_process.stdout)
        
        raw_title = metadata.get('title', 'video_download')
        
        # Regex to strip trailing IDs (e.g., -ABC123xyz) from the title
        cleaned_title = re.sub(r'([-\s]+)[\w-]{10,12}$', '', raw_title).strip()
        
        if not cleaned_title:
            cleaned_title = 'video_download'
        
    except subprocess.CalledProcessError as e:
        print(f"Metadata extraction error: {e.stderr}")
        return f"Error extracting video information. Please ensure the URL is valid. Error: {e.stderr.splitlines()[-1]}", 500
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return "Error processing video metadata.", 500

    # 3. Define output file path
    temp_base = str(uuid.uuid4())
    temp_filepath = os.path.join(DOWNLOAD_DIR, temp_base)
    
    final_download_name = f"{cleaned_title}.{format_ext}"
    
    # 4. Construct yt-dlp command for download
    # Use the cleaned URL for the download command as well
    command = ['yt-dlp', cleaned_url, '-o', f'{temp_filepath}.%(ext)s']

    # Set format-specific options
    output_ext = format_ext
    if format_ext == 'mp3':
        command.extend(['-x', '--audio-format', 'mp3', '--postprocessor-args', 'ffmpeg_i:-map_metadata 0'])
    elif format_ext == 'mp4':
        command.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])
    elif format_ext == 'webm':
        command.extend(['-f', 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best'])
    else:
        return f"Error: Unsupported format {format_ext}", 400

    # 5. Execute the download
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        # 6. Find the actual downloaded filename based on the temporary base name
        downloaded_file = next(
            (f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(temp_base) and f.endswith(f'.{output_ext}')), 
            None
        )

        if not downloaded_file:
            return "Error: Download failed to produce an output file.", 500
        
        full_path = os.path.join(DOWNLOAD_DIR, downloaded_file)

        # 7. Send the file to the user
        response = send_file(
            full_path,
            as_attachment=True,
            download_name=final_download_name
        )
        
        # 8. Clean up the temporary file after the response is sent
        @response.call_on_close
        def cleanup():
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Error cleaning up file {full_path}: {e}")
                
        return response

    except subprocess.CalledProcessError as e:
        print(f"yt-dlp error: {e.stderr}")
        return f"Download failed. Error: {e.stderr.splitlines()[-1]}", 500
    except Exception as e:
        print(f"Server error: {e}")
        return "An unexpected server error occurred.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
