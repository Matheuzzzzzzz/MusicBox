# app/config.py
import os

class Config:
    """Configurações da aplicação."""
    
    # Chave secreta usada para segurança de sessões e cookies.
    # Em produção, será lida de uma variável de ambiente.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-padrao'
    
    # URL de conexão com o banco de dados.
    # No Render, a plataforma irá definir a variável DATABASE_URL.
    # Localmente, a string pode ser ajustada.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciais do Spotify.
    # Em produção, estas serão lidas das variáveis de ambiente do Render.
    SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_URI') or 'http://127.0.0.1:5000/callback'