"""
Application entry point
"""
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import settings as app_settings


app = Flask(__name__)
app.config.from_object(app_settings.DevelopmentConfig)


@app.route('/')
def hello():
    """Test endpoint
    """
    return 'Hello World'


if __name__ == '__main__':
    app.run()
