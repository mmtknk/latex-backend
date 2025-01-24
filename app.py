import os
import subprocess
from flask import Flask, request, send_from_directory, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")  # Use the 'templates' folder for HTML files
CORS(app)

# Directory to store compiled PDFs
OUTPUT_DIR = "compiled_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def home():
    # Get a list of all PDF files in the OUTPUT_DIR
    pdf_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".pdf")]
    return render_template("index.html", pdf_files=pdf_files)

@app.route("/compile", methods=["POST"])
def compile_latex():
    # Handle LaTeX code from a form or API request
    latex_code = request.form.get("latex_code")
    file_name = request.form.get("file_name", "output")  # Default to "output" if not provided

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
        return jsonify({"message": f"PDF generated: {file_name}.pdf"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "LaTeX compilation failed", "details": e.stderr.decode()}), 500

@app.route("/pdfs/<path:filename>")
def serve_pdf(filename):
    # Serve a single PDF file from the OUTPUT_DIR
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
