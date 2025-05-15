from flask import Flask, request, render_template, send_file
import os
from pyDes import des, ECB, PAD_PKCS5
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        key = request.form.get("key")
        operation = request.form.get("operation")
        file = request.files.get("file")

        if not key or len(key) != 8:
            return render_template("index.html", message="Key must be 8 characters!", alert="danger")

        if not file:
            return render_template("index.html", message="Please upload a file!", alert="danger")

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        with open(input_path, 'rb') as f:
            data = f.read()

        k = des(key.encode(), ECB, padmode=PAD_PKCS5)

        if operation == "encrypt":
            processed_data = k.encrypt(data)
            result_filename = f"enc_{filename}"
        else:
            try:
                processed_data = k.decrypt(data)
            except:
                return render_template("index.html", message="Decryption failed. Invalid key or data!", alert="danger")
            result_filename = f"dec_{filename}"

        result_path = os.path.join(RESULT_FOLDER, result_filename)
        with open(result_path, 'wb') as f:
            f.write(processed_data)

        return render_template("index.html", message="Operation successful!", alert="success", download_file=result_filename)

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
