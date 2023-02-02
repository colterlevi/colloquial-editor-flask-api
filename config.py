import os

# Environment == The computer your app is running on
# with os.getenv we provide a variable name to look for on the computer
# if the variable is not found/undefined, set the second string as the value
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'abc123')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 'postgresql://colterlevi@localhost:5432/colloquial_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'youshallnotpass'
    DEBUG = True