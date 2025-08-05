import os

class Config:
    SECRET_KEY = os.environ.get('sua_senha_segura') or 'sua_senha_segura'
    
    # Use a string de conexão para MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://flaskuser:sua_senha_segura@localhost/music_box'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciais do Spotify
    SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_URI') or 'http://127.0.0.1:5000/callback'