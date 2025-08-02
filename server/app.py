from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../client/build', static_url_path='')

def serve_react_file(path='index.html'):
    """Helper function to serve React files"""
    static_folder = app.static_folder
    file_path = os.path.join(static_folder, path)
    
    # Debug logging
    print(f"Looking for file: {file_path}")
    print(f"Static folder: {static_folder}")
    print(f"Static folder exists: {os.path.exists(static_folder)}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    try:
        # Try to serve the requested file from the build directory
        return send_from_directory(static_folder, path)
    except FileNotFoundError:
        # If file not found, serve index.html (for client-side routing)
        index_path = os.path.join(static_folder, 'index.html')
        print(f"Fallback to index.html: {index_path}")
        print(f"Index.html exists: {os.path.exists(index_path)}")
        return send_from_directory(static_folder, 'index.html')

# Route for root URL (/)
@app.route('/', methods=['GET'])
def home():
    return serve_react_file('index.html')

# Route for all other paths (catch-all for React routing)
@app.route('/<path:path>', methods=['GET'])
def serve_react_path(path):
    return serve_react_file(path)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 for Render deployment
    app.run(host='0.0.0.0', port=port, debug=True)