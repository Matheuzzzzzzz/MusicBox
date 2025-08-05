import base64
import json
import requests
from flask import Blueprint, redirect, request, session, url_for, render_template
from models import db, Rating
from config import Config

# Define o Blueprint para as rotas
bp = Blueprint('routes', __name__)

# URLs da API do Spotify
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com'

@bp.route('/')
def index():
    """Rota da página inicial."""
    return render_template('index.html', access_token=session.get('access_token'))

@bp.route('/login')
def login():
    """Rota para iniciar o processo de login do Spotify."""
    scope = 'user-read-private user-read-email user-top-read'
    auth_url_with_params = (
        f"{AUTH_URL}?response_type=code&client_id={Config.CLIENT_ID}"
        f"&scope={scope}&redirect_uri={Config.REDIRECT_URI}"
    )
    return redirect(auth_url_with_params)

@bp.route('/callback')
def callback():
    """Rota de retorno após o login do Spotify."""
    if 'error' in request.args:
        return f"Erro de autenticação: {request.args['error']}"

    if 'code' in request.args:
        auth_code = request.args['code']
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': Config.REDIRECT_URI
        }
        
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(
                f"{Config.CLIENT_ID}:{Config.CLIENT_SECRET}".encode()
            ).decode()
        }
        
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        token_info = response.json()

        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['expires_in'] = token_info.get('expires_in')

        return redirect(url_for('routes.index'))
    return 'Erro: Nenhuma autorização de código recebida.'

@bp.route('/profile')
def get_user_profile():
    """Rota para exibir os dados do perfil do usuário."""
    if 'access_token' not in session:
        return redirect(url_for('routes.login'))
    
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    try:
        response = requests.get(f"{API_BASE_URL}/v1/me", headers=headers)
        response.raise_for_status()
        profile_data = response.json()
        
        return render_template('profile.html', user_data=profile_data)

    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 401:
            session.clear()
            return redirect(url_for('routes.login'))
        return render_template('profile.html', user_data=None)

@bp.route('/search', methods=['GET', 'POST'])
def search_songs():
    """Rota para buscar músicas e exibir os resultados."""
    if 'access_token' not in session:
        return redirect(url_for('routes.login'))

    tracks = []
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            return redirect(url_for('routes.search_songs'))

        headers = {'Authorization': f"Bearer {session['access_token']}"}
        params = {'q': query, 'type': 'track', 'limit': 10}

        try:
            response = requests.get(f"{API_BASE_URL}/v1/search", headers=headers, params=params)
            response.raise_for_status()
            results = response.json()
            tracks = results['tracks']['items']
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 401:
                session.clear()
                return redirect(url_for('routes.login'))
            return f"Erro ao buscar músicas: {e}"

    return render_template('search.html', tracks=tracks)

@bp.route('/rate/<track_id>', methods=['GET', 'POST'])
def rate_song(track_id):
    """Rota para avaliar uma música."""
    if 'access_token' not in session:
        return redirect(url_for('routes.login'))
    
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    
    # Busca os detalhes da música para obter o nome
    try:
        track_response = requests.get(f"{API_BASE_URL}/v1/tracks/{track_id}", headers=headers)
        track_response.raise_for_status()
        track_data = track_response.json()
        track_name = track_data['name']
    except requests.exceptions.RequestException as e:
        return f"Erro ao obter os detalhes da música: {e}"

    try:
        response = requests.get(f"{API_BASE_URL}/v1/me", headers=headers)
        response.raise_for_status()
        user_id = response.json()['id']
    except requests.exceptions.RequestException as e:
        return f"Erro ao obter o user_id: {e}"

    if request.method == 'POST':
        rating_value_str = request.form.get('rating')
        if not rating_value_str:
            return "Por favor, selecione uma nota."
        
        # AVALIAÇÃO AGORA É UM FLOAT PARA MEIAS ESTRELAS
        rating_value = float(rating_value_str) 
        
        existing_rating = Rating.query.filter_by(user_id=user_id, track_id=track_id).first()
        if existing_rating:
            return f"Você já avaliou a música '{track_name}' com a nota {existing_rating.rating}.<br><a href='{url_for('routes.index')}'>Voltar</a>"

        new_rating = Rating(user_id=user_id, track_id=track_id, rating=rating_value)
        try:
            db.session.add(new_rating)
            db.session.commit()
            return f"Sua avaliação de {rating_value} para a música '{track_name}' foi salva com sucesso!<br><a href='{url_for('routes.index')}'>Voltar</a>"
        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar a avaliação: {e}<br><a href='{url_for('routes.index')}'>Voltar</a>"

    return render_template('rate.html', track_id=track_id, track_name=track_name)

@bp.route('/logout')
def logout():
    """Rota para encerrar a sessão."""
    session.clear()
    return redirect(url_for('routes.index'))