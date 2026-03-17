from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Projet
from realisations.models import Realisation

def liste_projets(request):
    projets = Projet.objects.filter(statut__in=['attente', 'financement']).order_by('-date_creation')
    
    statut_filter = request.GET.get('statut')
    if statut_filter:
        projets = projets.filter(statut=statut_filter)
    
    return render(request, 'projets/liste_projets.html', {
        'projets': projets,
    })

def detail_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    
    pourcentage = 0
    if projet.budget_objectif > 0:
        pourcentage = (projet.montant_collecte / projet.budget_objectif) * 100
    
    return render(request, 'projets/detail_projet.html', {
        'projet': projet,
        'pourcentage': pourcentage,
    })

@login_required
def ajouter_projet(request):
    # Check if user has auteur role
    if request.user.role != 'auteur':
        messages.error(request, "Vous devez être Auteur/Réalisateur pour créer un projet de financement.")
        return redirect('projets:liste_projets')
    
    # Get available realisations
    realisations_disponibles = Realisation.objects.filter(
        utilise_pour_financement=False,
        est_publie=True,
        est_actif=True,
        auteur=request.user
    )
    
    if request.method == 'POST':
        realisation_id = request.POST.get('realisation')
        realisation = get_object_or_404(Realisation, id=realisation_id, auteur=request.user)
        
        projet = Projet(
            titre=request.POST.get('titre'),
            synopsis=request.POST.get('synopsis'),
            budget_objectif=request.POST.get('budget_objectif'),
            auteur=request.user,
            realisation_source=realisation,
            statut='attente',
        )
        if request.FILES.get('pre_affiche'):
            projet.pre_affiche = request.FILES.get('pre_affiche')
        projet.save()
        
        realisation.utilise_pour_financement = True
        realisation.save()
        
        messages.success(request, "Projet créé avec succès! En attente de validation.")
        return redirect('projets:detail_projet', id=projet.id)
    
    if not realisations_disponibles.exists():
        messages.warning(request, "Vous n'avez pas de réalisations disponibles pour financer un projet. Publiez d'abord un film.")
        return redirect('realisations:ajouter_realisation')
    
    return render(request, 'projets/ajouter_projet.html', {
        'realisations': realisations_disponibles,
    })
