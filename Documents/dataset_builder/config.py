import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'dataset.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add to your Config class
    UPLOAD_FOLDER = 'uploads'  # Path where the exported files will be saved

    
    # Load the SECRET_KEY from environment variable
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))  # Fallback to a random key if not set
