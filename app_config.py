# Enable dev. env.
DEBUG = True

# App's directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database info
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Applications threads.
THREADS_PER_PAGE = 2

# Cross-site request foregy protection
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'

# Secret key for signing cookies
SECRET_KEY = 'secret'