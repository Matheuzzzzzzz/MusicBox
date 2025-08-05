import os

class Config:
    """Configurações da aplicação."""
    
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-padrao'
    
   
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://flaskuser:sua_senha_segura@localhost/music_box'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SPOTIPY_CLIENT_ID = '795ced6b66a2492e83af41d542159fdb'
    SPOTIPY_CLIENT_SECRET = '53bb7256d91e48e9a8d04d41af92fe33'
    REDIRECT_URI = 'http://127.0.0.1:5000/callback'