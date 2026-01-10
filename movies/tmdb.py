import requests
from django.conf import settings

TMDB_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w200"  # taille affiches

def search_movies(query):
    response = requests.get(
        f"{TMDB_URL}/search/movie",
        params={
            "api_key": settings.TMDB_API_KEY,
            "query": query,
            "language": "fr-FR"
        }
    )
    data = response.json()
    return data.get("results", [])

def get_movie_details(tmdb_id):
    response = requests.get(
        f"{TMDB_URL}/movie/{tmdb_id}",
        params={
            "api_key": settings.TMDB_API_KEY,
            "language": "fr-FR"
        }
    )
    return response.json()  # contient titre, synopsis, genres, poster_path
