from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import Realisation
from communaute.models import Commentaire, Notation
from projets.models import Projet

COMMON_GENRES = [
    'Action', 'Drame', 'Comédie', 'Romance', 'Thriller', 'Science-Fiction',
    'Documentaire', 'Animation', 'Aventure', 'Horreur'
]


def index(request):
    films = Realisation.objects.filter(est_publie=True, est_actif=True).order_by('-date_creation')[:6]
    return render(request, 'realisations/index.html', {'films': films})


def liste_films(request):
    films = Realisation.objects.filter(est_publie=True, est_actif=True).order_by('-date_creation')
    
    genre_filter = request.GET.get('genre')
    if genre_filter:
        films = films.filter(genre=genre_filter)
    
    return render(request, 'realisations/liste_films.html', {
        'films': films,
        'genres': COMMON_GENRES,
    })


def detail_film(request, id):
    film = get_object_or_404(Realisation, id=id, est_actif=True)
    
    # Vérifier l'accès - seul l'auteur ou l'admin peut voir les films non publiés
    if not film.est_publie:
        # Vérifier si l'utilisateur est l'auteur ou admin
        if not request.user.is_authenticated:
            messages.error(request, "Ce film n'est pas disponible.")
            return redirect('realisations:liste_films')
        if request.user != film.auteur and not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Ce film n'est pas disponible.")
            return redirect('realisations:liste_films')
    
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
    if not request.user.peut_publier():
        messages.error(request, "Vous n'avez pas l'autorisation de publier des films.")
        return redirect('realisations:liste_films')

    if request.method == 'POST':
        realisation = Realisation(
            titre=request.POST.get('titre'),
            pitch=request.POST.get('pitch'),
            genre=request.POST.get('genre'),
            duree=request.POST.get('duree'),
            realisateur=request.POST.get('realisateur', ''),
            pays=request.POST.get('pays', ''),
            annee_production=request.POST.get('annee_production') or None,
            langue_originale=request.POST.get('langue_originale', ''),
            casting=request.POST.get('casting', ''),
            scenario=request.POST.get('scenario', ''),
            musique=request.POST.get('musique', ''),
            synopsis=request.POST.get('synopsis', ''),
            auteur=request.user,
            date_sortie=request.POST.get('date_sortie') or None,
            est_publie=False,
            est_brouillon=True,
            est_soumis=False,
        )
        if request.FILES.get('affiche'):
            realisation.affiche = request.FILES.get('affiche')
        if request.FILES.get('bande_annonce'):
            realisation.bande_annonce = request.FILES.get('bande_annonce')
        if request.FILES.get('video'):
            realisation.video = request.FILES.get('video')
        realisation.save()
        messages.success(request, "Film créé en brouillon! Soumettez-le pour validation quand vous êtes prêt.")
        return redirect('realisations:mes_realisations')
    return render(request, 'realisations/ajouter_realisation.html', {
        'genres': COMMON_GENRES,
    })


@login_required
def soumettre_realisation(request, id):
    """Soumettre une réalisation pour validation"""
    realisation = get_object_or_404(Realisation, id=id, auteur=request.user)
    
    if not realisation.est_brouillon:
        messages.warning(request, "Cette réalisation a déjà été soumise.")
        return redirect('realisations:mes_realisations')
    
    realisation.est_brouillon = False
    realisation.est_soumis = True
    realisation.save()
    
    # Envoyer email à l'admin
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f"[Karangou] Nouvelle réalisation à valider: {realisation.titre}",
                message=f"Une nouvelle réalisation a été soumise pour validation:\n\n"
                        f"Titre: {realisation.titre}\n"
                        f"Genre: {realisation.genre}\n"
                        f"Auteur: {realisation.auteur}\n\n"
                        f"Connectez-vous à l'admin pour la valider.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except:
        pass
    
    messages.success(request, "Réalisation soumise pour validation! L'administrateur va l'examiner.")
    return redirect('realisations:mes_realisations')


@login_required
def mes_realisations(request):
    """Réalisations de l'utilisateur connecté"""
    realisations = Realisation.objects.filter(auteur=request.user).order_by('-date_creation')
    return render(request, 'realisations/mes_realisations.html', {
        'realisations': realisations,
    })


@login_required
def modifier_realisation(request, id):
    """Modifier une réalisation en brouillon"""
    realisation = get_object_or_404(Realisation, id=id, auteur=request.user)
    
    if not realisation.est_brouillon:
        messages.warning(request, "Seuls les brouillons peuvent être modifiés.")
        return redirect('realisations:mes_realisations')
    
    if request.method == 'POST':
        realisation.titre = request.POST.get('titre')
        realisation.pitch = request.POST.get('pitch')
        realisation.genre = request.POST.get('genre')
        realisation.duree = request.POST.get('duree')
        realisation.realisateur = request.POST.get('realisateur', '')
        realisation.pays = request.POST.get('pays', '')
        realisation.annee_production = request.POST.get('annee_production') or None
        realisation.langue_originale = request.POST.get('langue_originale', '')
        realisation.casting = request.POST.get('casting', '')
        realisation.scenario = request.POST.get('scenario', '')
        realisation.musique = request.POST.get('musique', '')
        realisation.synopsis = request.POST.get('synopsis', '')
        realisation.date_sortie = request.POST.get('date_sortie') or None
        if request.FILES.get('affiche'):
            realisation.affiche = request.FILES.get('affiche')
        if request.FILES.get('bande_annonce'):
            realisation.bande_annonce = request.FILES.get('bande_annonce')
        if request.FILES.get('video'):
            realisation.video = request.FILES.get('video')
        realisation.save()
        messages.success(request, "Réalisation modifiée avec succès!")
        return redirect('realisations:mes_realisations')
    
    return render(request, 'realisations/modifier_realisation.html', {
        'realisation': realisation,
        'genres': COMMON_GENRES,
    })
