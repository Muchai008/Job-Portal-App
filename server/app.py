from flask import Flask, send_from_directory
import os

# Use build folder in same directory as app.py
app = Flask(__name__, static_folder='./build', static_url_path='')

def serve_react_file(path='index.html'):
    """Helper function to serve React files"""
    try:
        # Try to serve the requested file from the build directory
        return send_from_directory(app.static_folder, path)
    except FileNotFoundError:
        # If file not found, serve index.html (for client-side routing)
        return send_from_directory(app.static_folder, 'index.html')

# Route for root URL (/)
@app.route('/', methods=['GET'])
def home():
    return serve_react_file('index.html')

# Route for all other paths (catch-all for React routing)
@app.route('/<path:path>', methods=['GET'])
def serve_react_path(path):
    return serve_react_file(path)

if __name__ == '__main__':
    # Get port from environment variable (Render sets this to 10000 by default)
    port = int(os.environ.get('PORT', 10000))
    # Bind to 0.0.0.0 as required by Render
    app.run(host='0.0.0.0', port=port, debug=False)