import os


class Config(object):
    DEGUB = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BUCKET = os.environ.get('BUCKET')
    UPLOAD_FOLDER = 'uploads'

    db_provider = os.environ.get('DB_PROVIDER', 'mysql').lower()
    if db_provider == 'mysql':
        PONY = {
            'provider': os.environ.get('DB_PROVIDER', 'mysql'),
            'host': os.environ.get('DB_HOST', '0.0.0.0'),
            'user': os.environ.get('DB_USER', 'root'),
            'passwd': os.environ.get('DB_PASSWORD', 'PASSWORD'),
            'db': os.environ.get('DB_NAME', 'updog')
        }
    elif db_provider == 'postgres':
        PONY = {
            'provider': os.environ.get('DB_PROVIDER', 'mysql'),
            'host': os.environ.get('DB_HOST', '0.0.0.0'),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', 'PASSWORD'),
            'database': os.environ.get('DB_NAME', 'updog')
        }
    else:
        raise ValueError(f'Unknown database provider: {db_provider}')
        


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True