import os

class Config:
    """Configurações da aplicação."""
    
    # Chave secreta usada para segurança de sessões.
    # A prioridade é a variável de ambiente, com um fallback local.
    SECRET_KEY = os.environ.get('sua_senha_segura') or 'sua_senha_segura'
    
    # URL de conexão com o banco de dados.
    # O Render usa a variável DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get('https://MusicBox-1.onrender.com/callback')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciais do Spotify
    # As variáveis de ambiente do Render têm prioridade.
    SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_URI') or 'http://127.0.0.1:5000/callback'