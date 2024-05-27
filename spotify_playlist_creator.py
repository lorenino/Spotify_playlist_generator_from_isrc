import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm
import time
from requests.exceptions import ReadTimeout, RequestException
from spotipy.exceptions import SpotifyException
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration des variables d'environnement Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Scopes nécessaires pour créer une playlist et y ajouter des morceaux
scope = "playlist-modify-public"

# Authentification avec l'API Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

# Fonction pour gérer les retries
def with_retries(func, *args, retries=5, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except (ReadTimeout, RequestException, SpotifyException) as e:
            if isinstance(e, SpotifyException):
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 1))
                    print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                elif e.http_status == 502:
                    print(f"Bad Gateway (502). Retrying {attempt + 1}/{retries}...")
                    time.sleep(2 ** attempt)
                else:
                    print(f"Spotify exception: {e}")
            else:
                print(f"Error: {e}. Retrying {attempt + 1}/{retries}...")
                time.sleep(2 ** attempt)  # Exponential backoff
    raise Exception(f"Failed after {retries} retries.")

# Lecture du fichier CSV
file_path = input("Entrez le chemin du fichier CSV : ")
df = pd.read_csv(file_path)

# Vérifiez les colonnes présentes dans le fichier CSV
print("Colonnes disponibles dans le fichier CSV : ", df.columns)

# Demander le nom de la playlist
playlist_name = input("Entrez le nom de la nouvelle playlist : ")

# Création de la playlist avec retries
user_id = sp.me()['id']
playlist = with_retries(sp.user_playlist_create, user=user_id, name=playlist_name, public=True)

# Initialiser les barres de progression
total_tracks = len(df)
search_progress = tqdm(total=total_tracks, desc="Requêtes de recherche", position=0, leave=True)
found_progress = tqdm(total=0, desc="Titres trouvés", position=1, leave=True)
not_found_progress = tqdm(total=0, desc="Titres non trouvés", position=2, leave=True)

# Recherche des pistes et ajout à la playlist
track_uris = []
retry_limit = 5

for index, row in df.iterrows():
    isrc = row['ISRC']  # Assurez-vous que 'ISRC' est bien le nom de colonne correct
    query = f"isrc:{isrc}"
    success = False
    
    for attempt in range(retry_limit):
        try:
            result = with_retries(sp.search, q=query, type='track', limit=1)
            time.sleep(0.1)  # Petit délai pour éviter de surcharger l'API

            if not result or 'tracks' not in result or 'items' not in result['tracks']:
                not_found_progress.update(1)
                break

            tracks = result['tracks']['items']
            if not tracks:
                not_found_progress.update(1)
            else:
                if tracks[0] is not None and 'uri' in tracks[0]:
                    found_progress.update(1)
                    track_uris.append(tracks[0]['uri'])
                else:
                    not_found_progress.update(1)
            success = True
            break  # Sortir de la boucle de tentative si la requête a réussi

        except Exception as e:
            print(f"Error: {e}. Tentative {attempt + 1} de {retry_limit}.")
            time.sleep(2 ** attempt)  # Exponential backoff

    if not success:
        print(f"Échec de la requête pour ISRC: {isrc} après {retry_limit} tentatives.")
        not_found_progress.update(1)

    search_progress.update(1)

# Ajouter les pistes à la playlist par lots
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if track_uris:
    for i, chunk in enumerate(chunks(track_uris, 100)):
        with_retries(sp.playlist_add_items, playlist_id=playlist['id'], items=chunk)
    print(f"Playlist '{playlist_name}' créée avec succès!")
else:
    print("Aucune piste trouvée pour créer la playlist.")

# Fermer les barres de progression
search_progress.close()
found_progress.close()
not_found_progress.close()
