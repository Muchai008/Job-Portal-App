from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
import os
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecret')

#  Required for session cookies to work cross-origin
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True  # Must be True for cross-site cookies in modern browsers

# CORS (for local frontend at port 3000 or production)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000", 
    "https://your-frontend-on-render.com"  # Replace when deployed
])

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
