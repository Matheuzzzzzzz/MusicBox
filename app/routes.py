import requests
import base64
import spotipy
from flask import Blueprint, render_template, redirect, url_for, session, current_app, request, flash
from urllib.parse import urlencode
from datetime import datetime
from app.models import Rating, db

bp = Blueprint('routes', __name__)

@bp.route('/login')
def login():
    client_id = current_app.config['SPOTIPY_CLIENT_ID']
    redirect_uri = current_app.config['REDIRECT_URI']
    scopes = 'user-read-private user-read-email user-library-read playlist-read-private user-top-read'
    
    auth_url_base = 'https://accounts.spotify.com/authorize'
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scopes,
        'redirect_uri': redirect_uri
    }
    
    auth_url = f"{auth_url_base}?{urlencode(params)}"
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        flash("Autorização negada pelo Spotify.", "danger")
        return redirect(url_for('routes.index'))

    client_id = current_app.config['SPOTIPY_CLIENT_ID']
    client_secret = current_app.config['SPOTIPY_CLIENT_SECRET']
    redirect_uri = current_app.config['REDIRECT_URI']

    auth_str = f'{client_id}:{client_secret}'
    auth_bytes = auth_str.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    try:
        response = requests.post(token_url, data=body, headers=headers)
        response.raise_for_status()
        token_info = response.json()
        
        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        
        sp = spotipy.Spotify(auth=token_info.get('access_token'))
        user_info = sp.current_user()
        session['user_id'] = user_info.get('id')
        session['display_name'] = user_info.get('display_name')
        
        return redirect(url_for('routes.index'))

    except requests.exceptions.HTTPError as err:
        flash(f"Erro ao obter token do Spotify: {err}", "danger")
        return redirect(url_for('routes.index'))

@bp.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    session.pop('user_id', None)
    session.pop('display_name', None)
    flash("Você saiu com sucesso.", "success")
    return redirect(url_for('routes.index'))

def get_spotify_client():
    if 'access_token' in session:
        return spotipy.Spotify(auth=session['access_token'])
    return None

@bp.route('/')
def index():
    display_name = session.get('display_name')
    logged_in = 'access_token' in session
    return render_template('index.html', logged_in=logged_in, display_name=display_name)

def get_spotify_client():
    # Cria uma instância do cliente Spotify usando o token de acesso da sessão
    if 'access_token' in session:
        return spotipy.Spotify(auth=session['access_token'])
    return None

@bp.route('/search', methods=['GET'])
def search_tracks():
    sp = get_spotify_client()
    
    # Se não houver token, redireciona para o login
    if not sp:
        flash("Token de acesso expirado. Por favor, faça login novamente.", "warning")
        return redirect(url_for('routes.login'))
    
    query = request.args.get('query')
    if not query:
        # Se não houver uma query, renderiza a página de busca vazia
        return render_template('search.html', tracks=[])
    
    try:
        # Realiza a busca na API do Spotify
        results = sp.search(q=query, type='track', limit=10)
        tracks = results['tracks']['items']
        return render_template('results.html', tracks=tracks, query=query)
    except spotipy.exceptions.SpotifyException:
        flash("Token de acesso expirado. Por favor, faça login novamente.", "warning")
        return redirect(url_for('routes.login'))
    
@bp.route('/rate_song/<track_id>', methods=['GET', 'POST'])
def rate_song(track_id):
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('routes.login'))

    try:
        track = sp.track(track_id)
    except spotipy.exceptions.SpotifyException:
        flash("Token de acesso expirado. Por favor, faça login novamente.", "warning")
        return redirect(url_for('routes.login'))

    if request.method == 'POST':
        rating_value = request.form.get('rating')
        review = request.form.get('review')
        user_id = session.get('user_id')

        if not user_id or not rating_value:
            flash("Erro: Avaliação inválida.", "danger")
            return redirect(url_for('routes.index'))
        
        # Procura por uma avaliação existente para o mesmo usuário e música
        existing_rating = Rating.query.filter_by(user_id=user_id, track_id=track_id).first()
        if existing_rating:
            # Atualiza a avaliação existente
            existing_rating.rating_value = rating_value
            existing_rating.review = review
            existing_rating.timestamp = datetime.utcnow()
            flash("Sua avaliação foi atualizada com sucesso!", "success")
        else:
            # Cria uma nova avaliação
            new_rating = Rating(
                user_id=user_id,
                track_id=track_id,
                track_name=track['name'],
                artist_name=track['artists'][0]['name'],
                rating_value=rating_value,
                review=review
            )
            db.session.add(new_rating)
            flash("Sua avaliação foi salva com sucesso!", "success")
        
        db.session.commit()
        return redirect(url_for('routes.rated_songs_history'))
    
    return render_template('rate.html', track_id=track_id, track_name=track['name'], artist_name=track['artists'][0]['name'])

@bp.route('/history')
def rated_songs_history():
    
    user_id = session.get('user_id')
    
    
    if not user_id:
        return redirect(url_for('routes.login'))
    
   
    user_ratings = Rating.query.filter_by(user_id=user_id).order_by(Rating.timestamp.desc()).all()
    
    rated_tracks = []
    for rating in user_ratings:
        rated_tracks.append({
            'track_name': rating.track_name,
            'artist_name': rating.artist_name,
            'rating_value': rating.rating_value,
            'review': rating.review
        })
    
    return render_template('history.html', rated_tracks=rated_tracks)