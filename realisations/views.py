from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Realisation
from communaute.models import Commentaire, Notation
from projets.models import Projet

def index(request):
    films = Realisation.objects.filter(est_publie=True, est_actif=True).order_by('-date_creation')[:6]
    return render(request, 'realisations/index.html', {'films': films})

def liste_films(request):
    films = Realisation.objects.filter(est_publie=True, est_actif=True).order_by('-date_creation')
    genres = Realisation.objects.values_list('genre', flat=True).distinct()
    
    genre_filter = request.GET.get('genre')
    if genre_filter:
        films = films.filter(genre=genre_filter)
    
    return render(request, 'realisations/liste_films.html', {
        'films': films,
        'genres': genres,
    })

def detail_film(request, id):
    film = get_object_or_404(Realisation, id=id, est_actif=True)
    commentaires = Commentaire.objects.filter(film=film).order_by('-date')[:10]
    
    notations = Notation.objects.filter(film=film)
    note_data = notations.aggregate(avg_note=Avg('note'), count=Count('id'))
    note_moyenne = note_data['avg_note']
    nb_notes = note_data['count']
    note_entiere = int(round(note_moyenne)) if note_moyenne is not None else 0
    star_values = [5, 4, 3, 2, 1]
    star_values_display = [1, 2, 3, 4, 5]
    
    projet_associe = None
    try:
        projet_associe = Projet.objects.get(realisation_source=film)
    except Projet.DoesNotExist:
        pass
    
    note_utilisateur = None
    if request.user.is_authenticated:
        notation = Notation.objects.filter(film=film, utilisateur=request.user).first()
        if notation:
            note_utilisateur = notation.note
    
    return render(request, 'realisations/detail_film.html', {
        'film': film,
        'commentaires': commentaires,
        'note_moyenne': note_moyenne,
        'note_entiere': note_entiere,
        'star_values': star_values,
        'star_values_display': star_values_display,
        'nb_notes': nb_notes,
        'projet_associe': projet_associe,
        'note_utilisateur': note_utilisateur,
    })

@login_required
def ajouter_realisation(request):
    # Check if user has auteur or acteur role
    if request.user.role not in ['auteur', 'producteur']:
        messages.error(request, "Vous devez être Auteur/Réalisateur ou Producteur pour publier une réalisation.")
        return redirect('realisations:liste_films')
    
    # Liste de genres courants
    COMMON_GENRES = [
        'Action','Drame','Comédie','Romance','Thriller','Science-Fiction',
        'Documentaire','Animation','Aventure','Horreur'
    ]

    if request.method == 'POST':
        realisation = Realisation(
            titre=request.POST.get('titre'),
            description=request.POST.get('description'),
            genre=request.POST.get('genre'),
            duree=request.POST.get('duree'),
            auteur=request.user,
            date_sortie=request.POST.get('date_sortie'),
            est_publie=request.POST.get('est_publie') == 'on',
        )
        if request.FILES.get('affiche'):
            realisation.affiche = request.FILES.get('affiche')
        if request.FILES.get('video'):
            realisation.video = request.FILES.get('video')
        realisation.save()
        messages.success(request, "Réalisation ajoutée avec succès!")
        return redirect('realisations:detail_film', id=realisation.id)
    return render(request, 'realisations/ajouter_realisation.html', {
        'genres': COMMON_GENRES,
    })
