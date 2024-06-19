import os


def postgres_url():
    DB_USER = os.getenv('PGUSER')
    DB_PASSWORD = os.getenv('PGPASSWORD')
    DB_HOST = os.getenv('PGHOST')
    DB_NAME = os.getenv('PGDATABASE')
    url=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    return url