from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../client/build', static_url_path='')

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
    app.run(debug=True)