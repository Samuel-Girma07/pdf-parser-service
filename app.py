from flask import Flask, request, jsonify
import pdfplumber
import requests
from io import BytesIO
import os

app = Flask(__name__)

# Configuration
MAX_FILE_SIZE_MB = int(os.environ.get('MAX_FILE_SIZE_MB', '10'))
TIMEOUT_SECONDS = int(os.environ.get('TIMEOUT_SECONDS', '30'))


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'ok': True,
        'message': 'PDF Parser Service is running',
        'version': '1.0.0',
        'engine': 'pdfplumber'
    })


@app.route('/parse', methods=['POST'])
def parse_pdf():
    """
    Extract text from a PDF file using pdfplumber.

    Accepts JSON with either:
    - pdf_url: URL to download PDF from
    - pdf_base64: Base64 encoded PDF

    Returns:
    - text: Extracted text content
    - pages: Number of pages
    - success: True if successful
    - metadata: PDF metadata (title, author, etc.)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body must be JSON',
                'success': False
            }), 400

        # Support both URL and base64
        if 'pdf_url' in data:
            # Download PDF from URL
            try:
                response = requests.get(
                    data['pdf_url'],
                    timeout=TIMEOUT_SECONDS,
                    headers={
                        'User-Agent': 'PDF-Parser-Service/1.0'
                    }
                )
                response.raise_for_status()

                # Check file size
                content_length = len(response.content)
                max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
                if content_length > max_bytes:
                    return jsonify({
                        'error': f'PDF too large: {content_length / 1024 / 1024:.2f}MB (max: {MAX_FILE_SIZE_MB}MB)',
                        'success': False
                    }), 400

                pdf_file = BytesIO(response.content)
            except requests.exceptions.RequestException as e:
                return jsonify({
                    'error': f'Failed to download PDF: {str(e)}',
                    'success': False
                }), 500

        elif 'pdf_base64' in data:
            # Decode base64
            import base64
            try:
                pdf_bytes = base64.b64decode(data['pdf_base64'])

                # Check file size
                max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
                if len(pdf_bytes) > max_bytes:
                    return jsonify({
                        'error': f'PDF too large: {len(pdf_bytes) / 1024 / 1024:.2f}MB (max: {MAX_FILE_SIZE_MB}MB)',
                        'success': False
                    }), 400

                pdf_file = BytesIO(pdf_bytes)
            except Exception as e:
                return jsonify({
                    'error': f'Failed to decode base64: {str(e)}',
                    'success': False
                }), 400
        else:
            return jsonify({
                'error': 'Missing pdf_url or pdf_base64 in request body',
                'success': False
            }), 400

        # Parse PDF using pdfplumber for better text extraction
        try:
            texts = []
            with pdfplumber.open(pdf_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            texts.append({
                                'page': i + 1,
                                'text': text
                            })
                    except Exception as e:
                        # Skip pages that fail
                        print(f"Warning: Failed to extract text from page {i + 1}: {e}")

            numpages = len(pdf.pages) if 'pdf' in locals() else 0

        except Exception as e:
            return jsonify({
                'error': f'Failed to parse PDF: {str(e)}',
                'success': False
            }), 500

        # Combine all text
        full_text = '\n\n'.join([t['text'] for t in texts])

        if not full_text or len(full_text.strip()) == 0:
            return jsonify({
                'error': 'No text could be extracted from PDF. It may be a scanned image or contain only images.',
                'pages': numpages,
                'is_scanned': True,
                'success': False
            }), 400

        # Extract metadata (pdfplumber doesn't have metadata, return basic info)
        metadata = {
            'pages': numpages,
            'total_chars': len(full_text),
        }

        # Return successful response
        return jsonify({
            'success': True,
            'text': full_text,
            'pages': numpages,
            'is_scanned': False,
            'metadata': metadata,
            'chunks': [
                {
                    'page': t['page'],
                    'text': t['text'],
                    'char_count': len(t['text'])
                }
                for t in texts
            ]
        })

    except Exception as e:
        print(f"Unexpected error in /parse: {e}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'success': False
        }), 500


@app.route('/parse/info', methods=['GET'])
def parse_info():
    """Information about the service"""
    return jsonify({
        'service': 'PDF Parser Service',
        'version': '1.0.0',
        'engine': 'pdfplumber',
        'description': 'Extracts text from PDF files using pdfplumber (better than pypdf for complex PDFs)',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /parse': 'Extract text from PDF',
            'GET /parse/info': 'Service information'
        },
        'limits': {
            'max_file_size_mb': MAX_FILE_SIZE_MB,
            'timeout_seconds': TIMEOUT_SECONDS
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
