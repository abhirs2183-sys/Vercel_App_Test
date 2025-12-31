import os
import logging
from datetime import datetime
import pytz

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

def get_ist_now():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database Configuration
# Explicitly using the Neon URL provided by the user
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:npg_UVHTjef6Yv4D@ep-still-waterfall-a1jmfw19-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_number = db.Column(db.String(50), nullable=True)
    feedback_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=get_ist_now)

    def __init__(self, **kwargs):
        super(Feedback, self).__init__(**kwargs)

class UsageLog(db.Model):
    __tablename__ = 'usage_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.String(100), nullable=False)
    case_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=get_ist_now)

    def __init__(self, **kwargs):
        super(UsageLog, self).__init__(**kwargs)

# Create tables
with app.app_context():
    db.create_all()

from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
