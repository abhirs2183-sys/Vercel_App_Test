import os
import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
