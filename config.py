import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'techstore.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'techstore_secret_key_2024'
WTF_CSRF_ENABLED = True

# Flask-AppBuilder
AUTH_TYPE = 1  # DB Auth
AUTH_USER_REGISTRATION = False
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

FAB_API_MAX_PAGE_SIZE = 100
