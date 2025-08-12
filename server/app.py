import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from models import db, bcrypt

# Create Flask app
app = Flask(__name__, static_folder="./build", static_url_path="")

# ====================
# Configuration
# ====================
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///jobs.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
Session(app)
CORS(app, supports_credentials=True)

# ====================
# Import routes
# ====================
import routes  # noqa: E402

# ====================
# Serve React build
# ====================
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """
    Serves the React frontend for any non-API route.
    """
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Fallback to index.html for client-side routing
        return send_from_directory(app.static_folder, "index.html")

# ====================
# CLI command for local DB setup (not run in prod)
# ====================
@app.cli.command("create-db")
def create_db():
    """Create database tables."""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
