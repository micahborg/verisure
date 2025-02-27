from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Save the file temporarily
    temp_pdf_path = os.path.join(os.getcwd(), "temp_uploaded.pdf")
    file.save(temp_pdf_path)

    try:
        print(f"Processing file: {temp_pdf_path}")

        # Call the claim_extractor2.py script with the uploaded file
        result = subprocess.run(
            ["python", "claim_extractor2.py", temp_pdf_path],
            capture_output=True,
            text=True
        )

        print(f"Script output: {result.stdout}")
        print(f"Script error: {result.stderr}")

        if result.returncode != 0:
            return jsonify({"error": "Failed to process PDF", "details": result.stderr}), 500

        # Parse the JSON output from the script
        output = result.stdout
        return jsonify({"data": output}), 200

    except Exception as e:
        print(f"Error in Flask API: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up: Delete the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == '__main__':
    app.run(debug=True)