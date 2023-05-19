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
