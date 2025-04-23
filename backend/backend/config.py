import os

getenv = os.environ.get
db_user = getenv('DB_USER', 'postgres')
db_password = getenv('DB_PASSWORD', '')
db_host = getenv('DB_HOST', 'localhost')
db_port = getenv('DB_PORT', '5432')
db_name = getenv('DB_NAME', db_user)

SQLALCHEMY_DATABASE_URI = (
    f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
)
SECRET_KEY = getenv('SECRET_KEY')
ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')
ENABLE_DOCS = getenv('ENABLE_DOCS')
EMAIL_HOST = getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = getenv('EMAIL_PORT', 25)
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER', 'dev@localhost')
EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = bool(getenv('EMAIL_USE_TLS', False))
EMAIL_USE_SSL = bool(getenv('EMAIL_USE_SSL', False))
STREAM_REFRESH_INTERVAL = float(getenv('STREAM_REFRESH_INTERVAL', 1))
