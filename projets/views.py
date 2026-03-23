from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Projet
from realisations.models import Realisation


def liste_projets(request):
    """Liste des projets visibles par tous (publiés uniquement)"""
    projets = Projet.objects.filter(
        est_brouillon=False,
        est_soumis=True,
        statut__in=['financement', 'finance']
    ).exclude(
        date_fin__lt=timezone.now().date()
    ).order_by('-date_creation')
    
    statut_filter = request.GET.get('statut')
    if statut_filter:
        projets = projets.filter(statut=statut_filter)
    
    return render(request, 'projets/liste_projets.html', {
        'projets': projets,
    })


def detail_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    
    # Vérifier l'accès - seul l'auteur ou l'admin peut voir les projets non validés
    if not (projet.est_soumis and projet.statut in ['financement', 'finance']):
        # Vérifier si l'utilisateur est l'auteur ou admin
        if not request.user.is_authenticated:
            messages.error(request, "Ce projet n'est pas disponible.")
            return redirect('projets:liste_projets')
        if request.user != projet.auteur and not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Ce projet n'est pas disponible.")
            return redirect('projets:liste_projets')
    
    # Vérifier que le film source est publié
    if not projet.realisation_source.est_publie and (not request.user.is_authenticated or request.user != projet.auteur):
        if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
            messages.error(request, "Le film associé n'est pas encore disponible.")
            return redirect('projets:liste_projets')
    
    if projet.est_expire and projet.statut == 'financement':
        projet.statut = 'annule'
        projet.save()
    
    pourcentage = projet.pourcentage
    
    return render(request, 'projets/detail_projet.html', {
        'projet': projet,
        'pourcentage': pourcentage,
    })


@login_required
def ajouter_projet(request):
    """Créer un nouveau projet (en brouillon)"""
    if not request.user.peut_publier():
        messages.error(request, "Vous n'avez pas l'autorisation de créer des projets.")
        return redirect('projets:liste_projets')
    
    realisations_disponibles = Realisation.objects.filter(
        utilise_pour_financement=False,
        est_publie=True,
        est_actif=True,
        auteur=request.user
    )
    
    if request.method == 'POST':
        realisation_id = request.POST.get('realisation')
        realisation = get_object_or_404(Realisation, id=realisation_id, auteur=request.user)
        
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        projet = Projet(
            titre=request.POST.get('titre'),
            synopsis=request.POST.get('synopsis'),
            description=request.POST.get('description', ''),
            genre=request.POST.get('genre', ''),
            budget_objectif=request.POST.get('budget_objectif'),
            auteur=request.user,
            realisation_source=realisation,
            date_debut=date_debut if date_debut else None,
            date_fin=date_fin if date_fin else None,
            statut='attente',
            est_brouillon=True,
            est_soumis=False,
        )
        if request.FILES.get('pre_affiche'):
            projet.pre_affiche = request.FILES.get('pre_affiche')
        projet.save()
        
        messages.success(request, "Projet créé en brouillon. Soumettez-le pour validation quand vous êtes prêt.")
        return redirect('projets:mes_projets')
    
    if not realisations_disponibles.exists():
        messages.warning(request, "Vous n'avez pas de réalisations disponibles pour financer un projet.")
        return redirect('realisations:ajouter_realisation')
    
    return render(request, 'projets/ajouter_projet.html', {
        'realisations': realisations_disponibles,
    })


@login_required
def soumettre_projet(request, id):
    """Soumettre un projet pour validation"""
    projet = get_object_or_404(Projet, id=id, auteur=request.user)
    
    if not projet.est_brouillon:
        messages.warning(request, "Ce projet a déjà été soumis.")
        return redirect('projets:mes_projets')
    
    projet.est_brouillon = False
    projet.est_soumis = True
    projet.save()
    
    # Envoyer email à l'admin
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f"[Karangou] Nouveau projet à valider: {projet.titre}",
                message=f"Un nouveau projet a été soumis pour validation:\n\n"
                        f"Titre: {projet.titre}\n"
                        f"Auteur: {projet.auteur}\n"
                        f"Budget: {projet.budget_objectif} Fcfa\n\n"
                        f"Connectez-vous à l'admin pour le valider.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except:
        pass
    
    messages.success(request, "Projet soumis pour validation! L'administrateur va l'examiner.")
    return redirect('projets:mes_projets')


@login_required
def mes_projets(request):
    """Projets de l'utilisateur connecté (tous ses projets)"""
    projets = Projet.objects.filter(auteur=request.user).order_by('-date_creation')
    return render(request, 'projets/mes_projets.html', {
        'projets': projets,
    })


@login_required
def modifier_projet(request, id):
    """Modifier un projet en brouillon"""
    projet = get_object_or_404(Projet, id=id, auteur=request.user)
    
    if not projet.est_brouillon:
        messages.warning(request, "Seuls les brouillons peuvent être modifiés.")
        return redirect('projets:mes_projets')
    
    realisations_disponibles = Realisation.objects.filter(
        utilise_pour_financement=False,
        est_publie=True,
        est_actif=True,
        auteur=request.user
    )
    
    if request.method == 'POST':
        projet.titre = request.POST.get('titre')
        projet.synopsis = request.POST.get('synopsis')
        projet.description = request.POST.get('description', '')
        projet.genre = request.POST.get('genre', '')
        projet.budget_objectif = request.POST.get('budget_objectif')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        projet.date_debut = date_debut if date_debut else None
        projet.date_fin = date_fin if date_fin else None
        if request.FILES.get('pre_affiche'):
            projet.pre_affiche = request.FILES.get('pre_affiche')
        projet.save()
        messages.success(request, "Projet modifié avec succès!")
        return redirect('projets:mes_projets')
    
    return render(request, 'projets/modifier_projet.html', {
        'projet': projet,
        'realisations': realisations_disponibles,
    })
