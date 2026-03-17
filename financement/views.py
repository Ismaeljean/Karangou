from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from projets.models import Projet
from .models import Contribution

@login_required
def contribuer(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    
    if request.method == 'POST':
        montant = request.POST.get('montant')
        moyen_paiement = request.POST.get('moyen_paiement', 'mobile_money')
        
        try:
            montant = float(montant)
            if montant <= 0:
                messages.error(request, "Le montant doit être positif.")
                return redirect('projets:detail_projet', id=projet_id)
        except ValueError:
            messages.error(request, "Montant invalide.")
            return redirect('projets:detail_projet', id=projet_id)
        
        # Créer la contribution
        contribution = Contribution(
            utilisateur=request.user,
            projet=projet,
            montant=montant,
            moyen_paiement=moyen_paiement,
        )
        contribution.save()
        
        # Mettre à jour le montant collecté
        projet.montant_collecte += montant
        if projet.montant_collecte >= projet.budget_objectif:
            projet.statut = 'finance'
        elif projet.statut == 'attente':
            projet.statut = 'financement'
        projet.save()
        
        messages.success(request, f"Merci pour votre contribution de {montant}€!")
        return redirect('financement:mes_contributions')
    
    return redirect('projets:detail_projet', id=projet_id)

@login_required
def mes_contributions(request):
    contributions = Contribution.objects.filter(utilisateur=request.user).order_by('-date_contribution')
    return render(request, 'financement/mes_contributions.html', {
        'contributions': contributions
    })
