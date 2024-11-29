from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "codigo"))

from main import main

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process_text():
    try:
        data = request.json
        input_text = data.get('input_text', '')

        # Chama a função main
        results = main(input_text)

        return jsonify({'resultados': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
