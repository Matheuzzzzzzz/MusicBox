import os

class Config:
    SECRET_KEY = os.urandom(24)
    CLIENT_ID = '795ced6b66a2492e83af41d542159fdb'
    CLIENT_SECRET = '53bb7256d91e48e9a8d04d41af92fe33'
    REDIRECT_URI = 'http://127.0.0.1:5000/callback'
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/spotify_ratings'
    SQLALCHEMY_TRACK_MODIFICATIONS = False