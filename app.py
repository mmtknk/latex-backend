import os
import subprocess
from flask import Flask, request, send_file, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests if needed

# Directory to store compiled PDFs
OUTPUT_DIR = "compiled_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/compile", methods=["POST"])
def compile_latex():
    data = request.json
    latex_code = data.get("latex_code")
    file_name = data.get("file_name", "output")  # Default to "output" if not provided

    if not latex_code:
        return jsonify({"error": "No LaTeX code provided"}), 400

    # Save LaTeX code to a .tex file
    tex_file = os.path.join(OUTPUT_DIR, f"{file_name}.tex")
    with open(tex_file, "w") as f:
        f.write(latex_code)

    # Compile LaTeX file using pdflatex
    try:
        subprocess.run(
            ["pdflatex", "-output-directory", OUTPUT_DIR, tex_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        pdf_file = os.path.join(OUTPUT_DIR, f"{file_name}.pdf")
        if os.path.exists(pdf_file):
            return send_file(pdf_file, as_attachment=True)
        else:
            return jsonify({"error": "PDF not generated"}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "LaTeX compilation failed", "details": e.stderr.decode()}), 500

# Serve compiled PDFs directly via HTTP
@app.route("/pdfs/<path:filename>", methods=["GET"])
def serve_pdf(filename):
    try:
        return send_from_directory(OUTPUT_DIR, filename)
    except FileNotFoundError:
        return jsonify({"error": f"File '{filename}' not found"}), 404

@app.route("/", methods=["GET"])
def home():
    return "Flask app for LaTeX compilation is running! Access /compile for LaTeX or /pdfs/<filename> for PDFs."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Expose the app on all interfaces

