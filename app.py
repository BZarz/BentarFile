import os, uuid, threading, time
from flask import Flask, request, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "mp4", "pptx", "py", "zip"}
EXPIRATION_TIME = 600  # 10 menit

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_delete(filepath, delay):
    time.sleep(delay)
    if os.path.exists(filepath):
        os.remove(filepath)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Tambahkan timestamp ke nama file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        final_name = f"{name}-{timestamp}{ext}"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], final_name)
        file.save(filepath)

        threading.Thread(target=auto_delete, args=(filepath, EXPIRATION_TIME)).start()
        return jsonify({'download_url': f"/uploads/{final_name}"})
    return jsonify({'error': 'Invalid file'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

