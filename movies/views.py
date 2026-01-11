from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from .models import Film, Note
from .forms import FilmForm, TMDBSearchForm, NoteForm
from .tmdb import search_movies, get_movie_details
import json
from datetime import date

# Page d'accueil : liste des films
@login_required
def film_list(request):
    # Année sélectionnée depuis GET
    annee_filter = request.GET.get('annee', str(date.today().year))

    # Liste des années existantes pour les films
    films_existants = Film.objects.exclude(date_visionnage__isnull=True)
    annees_list = films_existants.dates('date_visionnage', 'year', order='DESC')
    if not annees_list:
        annees_list = [date.today()]

    # Convertir en int/année
    annees = [d.year for d in annees_list]

    # Ajouter l'année en cours en première position si elle n'est pas déjà dans la liste
    current_year = date.today().year
    if current_year not in annees:
        annees = [current_year] + annees
    else:
        # Placer l'année en cours en tête
        annees = [current_year] + [y for y in annees if y != current_year]

    # Filtrer les films
    if annee_filter == "":
        films = Film.objects.filter(utilisateur=request.user).order_by('ordre')
    else:
        films = Film.objects.filter(date_visionnage__year=annee_filter, utilisateur=request.user).order_by('ordre')

    context = {
        'films': films,
        'annees': annees,
        'annee_filter': annee_filter,
    }
    return render(request, 'movies/film_list.html', context)

# Ajouter un film avec recherche TMDB
@login_required
def film_add(request):
    search_form = TMDBSearchForm()
    film_form = None
    search_results = []
    selected_movie = None

    if request.method == "POST":
        # 🔍 Recherche TMDB
        if "search_tmdb" in request.POST:
            search_form = TMDBSearchForm(request.POST)
            if search_form.is_valid():
                query = search_form.cleaned_data["query"]
                search_results = search_movies(query)

        # 🎯 Sélectionner un film pour voir détails
        elif "select_movie" in request.POST:
            tmdb_id = request.POST.get("tmdb_id")
            selected_movie = get_movie_details(tmdb_id)
            film_form = FilmForm(initial={
                "titre": selected_movie.get("title", ""),
                "annee": selected_movie.get("release_date", "")[:4],
                "genre": ", ".join([g["name"] for g in selected_movie.get("genres", [])])
            })

        # 💾 Sauvegarder le film et la note
        elif "save_film" in request.POST:
            film_form = FilmForm(request.POST)
            if film_form.is_valid():
                film = film_form.save(commit=False)
                film.utilisateur = request.user

                tmdb_id = request.POST.get("tmdb_id")
                if tmdb_id:
                    movie = get_movie_details(tmdb_id)
                    film.synopsis = movie.get("overview", "")
                    film.titre = movie.get("original_title", "")
                    film.releasedate = movie.get("release_date", "")
                    poster_path = movie.get("poster_path")
                    if poster_path:
                        film.poster_url = "https://image.tmdb.org/t/p/w300" + poster_path

                film.save()

                # Créer la note
                note_value = float(request.POST.get("note", 3))
                Note.objects.create(film=film, utilisateur=request.user, note=note_value)

                messages.success(request, f'Film "{film.titre}" ajouté avec succès.')
                return redirect("film_list")


    return render(request, "movies/film_add.html", {
        "search_form": search_form,
        "film_form": film_form,
        "search_results": search_results,
        "selected_movie": selected_movie,
    })

# Page détail du film
@login_required
def film_detail(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    note, _ = Note.objects.get_or_create(film=film, utilisateur=request.user, defaults={'note': 3})

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, f'Votre note pour "{film.titre}" a été mise à jour')
            return redirect('film_detail', film_id=film.id)
    else:
        form = NoteForm(instance=note)

    return render(request, 'movies/film_detail.html', {
        "film": film,
        "note": note,
        "form": form
    })

# Supprimer un film
@login_required
def film_delete(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if request.method == "POST":
        film.delete()
        messages.success(request, f'Le film "{film.titre}" a été supprimé')
        return redirect("film_list")
    return render(request, "movies/film_confirm_delete.html", {"film": film})

@login_required
@csrf_exempt  # On va utiliser AJAX
def update_order(request):
    if request.method == "POST":
        # On attend un JSON : {"order": [3,1,2,...]}
        import json
        data = json.loads(request.body)
        new_order = data.get("order", [])
        for index, film_id in enumerate(new_order):
            Film.objects.filter(id=film_id).update(ordre=index)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connecte automatiquement l’utilisateur
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé.")
            return redirect('film_list')
    else:
        form = UserCreationForm()
    return render(request, 'movies/signup.html', {'form': form})

@login_required
@csrf_exempt
def film_reorder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
            for position, film_id in enumerate(order_list):
                Film.objects.filter(id=film_id, utilisateur=request.user).update(ordre=position)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

def classement(request):
    annee_filter = request.GET.get("annee")
    if not annee_filter:
        annee_filter = str(date.today().year)
    annees = Film.objects.dates('date_visionnage', 'year', order='DESC')

    films = Film.objects.filter(date_visionnage__year=annee_filter).select_related('utilisateur')

    points_par_position = [50, 40, 30, 20, 10]

    # score total par titre
    scores = defaultdict(int)

    # utilisateurs distincts par titre
    viewers = defaultdict(set)

    # film "référence" par titre (pour affiche, synopsis)
    films_info = {}

    for film in films:
        user_films = list(
            Film.objects
            .filter(utilisateur=film.utilisateur)
            .order_by('ordre')
        )

        try:
            position = user_films.index(film)
        except ValueError:
            continue

        if position < len(points_par_position):
            scores[film.titre] += points_par_position[position]

        viewers[film.titre].add(film.utilisateur.id)

        if film.titre not in films_info:
            films_info[film.titre] = film

    # Construction du classement final
    classement_films = []

    for titre, score_total in scores.items():
        nb_viewers = len(viewers[titre])
        score_moyen = round(score_total*2 / nb_viewers, 1) if nb_viewers > 0 else 0

        classement_films.append({
            'titre': titre,
            'film': films_info[titre],
            'score': score_moyen,
            'nb_viewers': nb_viewers,
        })

    classement_films.sort(key=lambda x: x['score'], reverse=True)

    return render(
        request,
        "movies/classement.html",
        {"annees": annees, "annee_filter": annee_filter, "classement_films": classement_films}
    )
