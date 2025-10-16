# Vercel-compatible Flask app for serving hosted files (no Telegram polling)
# Uses environment variables for configuration. Designed for Vercel serverless functions.
from flask import Flask, jsonify, send_file, abort
import os
import hashlib
from pathlib import Path

app = Flask(__name__)

# Configuration via environment variables
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "uploads")
BASE_URL = os.environ.get("BASE_URL", "")  # optional, used to display file URLs

# Ensure uploads directory exists
Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

# Simple in-memory index loader (loads at startup from disk)
def load_index():
    index = {}
    uploads = Path(UPLOADS_DIR)
    for uid_folder in uploads.iterdir():
        if not uid_folder.is_dir(): 
            continue
        user_id = uid_folder.name
        for f in uid_folder.iterdir():
            if f.is_file():
                file_hash = hashlib.md5(f"{user_id}_{f.name}".encode()).hexdigest()
                index[file_hash] = {
                    "user_id": user_id,
                    "file_name": f.name,
                    "path": str(f.resolve())
                }
    return index

FILE_INDEX = load_index()

@app.route("/")
def home():
    return """
    <html>
      <head><title>Universal File Host (Vercel)</title></head>
      <body style="font-family: Arial, sans-serif; text-align:center; padding:40px;">
        <h1>Universal File Host (Vercel)</h1>
        <p>This is a <strong>Flask-only</strong> file hosting service meant to be deployed on Vercel as a serverless function.</p>
        <p>Upload and management of files must be done externally (e.g., via another service or a separate background worker).</p>
        <p>Environment variables:<br>UPLOADS_DIR (default: uploads)</p>
      </body>
    </html>
    """

@app.route("/health")
def health():
    return jsonify({"status":"healthy", "version":"vercel-flask-1.0"})

@app.route("/files")
def list_files():
    # Return a list of hosted files and their URLs
    files = []
    base = BASE_URL.rstrip("/") if BASE_URL else ""
    for h, meta in FILE_INDEX.items():
        url = f"{base}/api/file/{h}" if base else f"/api/file/{h}"
        files.append({
            "hash": h,
            "user_id": meta["user_id"],
            "file_name": meta["file_name"],
            "url": url
        })
    return jsonify({"files": files})

@app.route("/file/<file_hash>")
def serve_file(file_hash):
    meta = FILE_INDEX.get(file_hash)
    if not meta:
        abort(404, description="File not found")
    path = meta["path"]
    if not os.path.exists(path):
        abort(404, description="File missing on disk")
    # send_file will stream the file
    return send_file(path, conditional=True)

# Vercel expects a WSGI entrypoint at the module level (app)
# If running locally: flask run --port 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
