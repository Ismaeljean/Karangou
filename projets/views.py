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
        est_soumis=False,
        statut__in=['financement', 'finance'],
        realisation_source__est_publie=True
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
    from communaute.models import Commentaire
    
    projet = get_object_or_404(Projet, id=id)
    
    if not (projet.est_soumis and projet.statut in ['financement', 'finance']):
        if not request.user.is_authenticated:
            messages.error(request, "Ce projet n'est pas disponible.")
            return redirect('projets:liste_projets')
        if request.user != projet.auteur and not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Ce projet n'est pas disponible.")
            return redirect('projets:liste_projets')
    
    if not projet.realisation_source.est_publie and (not request.user.is_authenticated or request.user != projet.auteur):
        if not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
            messages.error(request, "Le film associé n'est pas encore disponible.")
            return redirect('projets:liste_projets')
    
    if projet.est_expire and projet.statut == 'financement':
        projet.statut = 'annule'
        projet.save()
    
    pourcentage = projet.pourcentage
    commentaires = Commentaire.objects.filter(projet=projet, parent__isnull=True).order_by('date')
    auteurs_invites_ids = list(projet.auteurs_invites.values_list('id', flat=True))
    acteurs_invites_ids = list(projet.acteurs_invites.values_list('id', flat=True))
    
    return render(request, 'projets/detail_projet.html', {
        'projet': projet,
        'pourcentage': pourcentage,
        'commentaires': commentaires,
        'auteurs_invites_ids': auteurs_invites_ids,
        'acteurs_invites_ids': acteurs_invites_ids,
    })


@login_required
def ajouter_projet(request):
    """Créer un nouveau projet (en brouillon)"""
    if not request.user.peut_publier():
        messages.error(request, "Vous n'avez pas l'autorisation de créer des projets.")
        return redirect('projets:liste_projets')
    
    realisation_id = request.GET.get('realisation_id')
    realisation_preselectionnee = None
    
    if realisation_id:
        try:
            realisation_preselectionnee = Realisation.objects.get(
                id=realisation_id, 
                auteur=request.user,
                est_actif=True
            )
        except Realisation.DoesNotExist:
            messages.error(request, "Réalisation non trouvée ou non accessible.")
            return redirect('realisations:mes_realisations')
    
    realisations_disponibles = Realisation.objects.filter(
        utilise_pour_financement=False,
        est_actif=True,
        auteur=request.user
    ).exclude(est_soumis=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        realisation_id_post = request.POST.get('realisation') or realisation_id
        
        if not realisation_id_post:
            messages.error(request, "Vous devez sélectionner une réalisation.")
            return render(request, 'projets/ajouter_projet.html', {
                'realisations': realisations_disponibles,
                'realisation_preselectionnee': realisation_preselectionnee,
            })
        
        realisation = get_object_or_404(Realisation, id=realisation_id_post, auteur=request.user)
        
        if realisation.utilise_pour_financement:
            messages.error(request, "Cette réalisation est déjà utilisée pour un autre projet de financement.")
            return render(request, 'projets/ajouter_projet.html', {
                'realisations': realisations_disponibles,
                'realisation_preselectionnee': realisation_preselectionnee,
            })
        
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        nom_banque = request.POST.get('nom_banque', '').strip()
        numero_compte = request.POST.get('numero_compte', '').strip()
        titulaire_compte = request.POST.get('titulaire_compte', '').strip()
        rib_document = request.FILES.get('rib_document')
        
        errors = []
        if not nom_banque:
            errors.append("Le nom de la banque est obligatoire.")
        if not numero_compte:
            errors.append("Le numéro de compte est obligatoire.")
        if not titulaire_compte:
            errors.append("Le titulaire du compte est obligatoire.")
        if not rib_document:
            errors.append("Le RIB est obligatoire.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'projets/ajouter_projet.html', {
                'realisations': realisations_disponibles,
                'realisation_preselectionnee': realisation_preselectionnee,
            })
        
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
            nom_banque=nom_banque,
            numero_compte=numero_compte,
            titulaire_compte=titulaire_compte,
        )
        if request.FILES.get('pre_affiche'):
            projet.pre_affiche = request.FILES.get('pre_affiche')
        projet.rib_document = rib_document
        
        realisation.utilise_pour_financement = True
        realisation.save()
        
        projet.save()
        
        if action == 'soumettre':
            realisation.est_brouillon = False
            realisation.est_soumis = True
            realisation.save()
            
            projet.est_brouillon = False
            projet.est_soumis = True
            projet.save()
            
            try:
                admin_email = getattr(settings, 'ADMIN_EMAIL', None)
                if admin_email:
                    send_mail(
                        subject=f"[Karangou] Nouvelle paire (réalisation + projet) à valider",
                        message=f"Une nouvelle réalisation et son projet de financement ont été soumis pour validation:\n\n"
                                f"Réalisation: {realisation.titre}\n"
                                f"Genre: {realisation.genre}\n"
                                f"Auteur: {realisation.auteur}\n\n"
                                f"Projet: {projet.titre}\n"
                                f"Budget: {projet.budget_objectif} Fcfa\n\n"
                                f"Connectez-vous à l'admin pour les valider.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin_email],
                        fail_silently=True,
                    )
            except:
                pass
            
            messages.success(request, "Réalisation et projet soumis pour validation! L'administrateur va les examiner.")
        else:
            messages.success(request, "Projet créé en brouillon. Soumettez-le pour validation quand vous êtes prêt.")
        
        return redirect('projets:mes_projets')
    
    if not realisation_preselectionnee and not realisations_disponibles.exists():
        messages.warning(request, "Vous n'avez pas de réalisations disponibles pour financer un projet.")
        return redirect('realisations:ajouter_realisation')
    
    return render(request, 'projets/ajouter_projet.html', {
        'realisations': realisations_disponibles,
        'realisation_preselectionnee': realisation_preselectionnee,
    })


@login_required
def soumettre_projet(request, id):
    """Soumettre un projet et sa réalisation associée pour validation"""
    projet = get_object_or_404(Projet, id=id, auteur=request.user)
    
    if not projet.est_brouillon:
        messages.warning(request, "Ce projet a déjà été soumis.")
        return redirect('projets:mes_projets')
    
    realisation = projet.realisation_source
    
    if realisation.est_soumis:
        messages.warning(request, "La réalisation associée a déjà été soumise.")
        return redirect('projets:mes_projets')
    
    realisation.est_brouillon = False
    realisation.est_soumis = True
    realisation.save()
    
    projet.est_brouillon = False
    projet.est_soumis = True
    projet.save()
    
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f"[Karangou] Nouvelle paire (réalisation + projet) à valider",
                message=f"Une réalisation et son projet de financement ont été soumis pour validation:\n\n"
                        f"Réalisation: {realisation.titre}\n"
                        f"Genre: {realisation.genre}\n"
                        f"Auteur: {realisation.auteur}\n\n"
                        f"Projet: {projet.titre}\n"
                        f"Budget: {projet.budget_objectif} Fcfa\n\n"
                        f"Connectez-vous à l'admin pour les valider.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except:
        pass
    
    messages.success(request, "Réalisation et projet soumis pour validation! L'administrateur va les examiner.")
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
        est_actif=True,
        auteur=request.user
    ).exclude(est_soumis=True).exclude(
        utilise_pour_financement=True
    )
    
    if request.method == 'POST':
        new_realisation_id = request.POST.get('realisation')
        
        if new_realisation_id:
            new_realisation = get_object_or_404(Realisation, id=new_realisation_id, auteur=request.user)
            
            if new_realisation_id != str(projet.realisation_source.id):
                if new_realisation.utilise_pour_financement:
                    messages.error(request, "Cette réalisation est déjà utilisée pour un autre projet de financement.")
                    return render(request, 'projets/modifier_projet.html', {
                        'projet': projet,
                        'realisations': realisations_disponibles,
                    })
                
                old_realisation = projet.realisation_source
                old_realisation.utilise_pour_financement = False
                old_realisation.save()
                
                projet.realisation_source = new_realisation
                new_realisation.utilise_pour_financement = True
                new_realisation.save()
        
        nom_banque = request.POST.get('nom_banque', '').strip()
        numero_compte = request.POST.get('numero_compte', '').strip()
        titulaire_compte = request.POST.get('titulaire_compte', '').strip()
        rib_document = request.FILES.get('rib_document')
        
        errors = []
        if not nom_banque:
            errors.append("Le nom de la banque est obligatoire.")
        if not numero_compte:
            errors.append("Le numéro de compte est obligatoire.")
        if not titulaire_compte:
            errors.append("Le titulaire du compte est obligatoire.")
        if not rib_document and not projet.rib_document:
            errors.append("Le RIB est obligatoire.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'projets/modifier_projet.html', {
                'projet': projet,
                'realisations': realisations_disponibles,
            })
        
        projet.titre = request.POST.get('titre')
        projet.synopsis = request.POST.get('synopsis')
        projet.description = request.POST.get('description', '')
        projet.genre = request.POST.get('genre', '')
        projet.budget_objectif = request.POST.get('budget_objectif')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        projet.date_debut = date_debut if date_debut else None
        projet.date_fin = date_fin if date_fin else None
        projet.nom_banque = nom_banque
        projet.numero_compte = numero_compte
        projet.titulaire_compte = titulaire_compte
        if request.FILES.get('pre_affiche'):
            projet.pre_affiche = request.FILES.get('pre_affiche')
        if rib_document:
            projet.rib_document = rib_document
        projet.save()
        messages.success(request, "Projet modifié avec succès!")
        return redirect('projets:mes_projets')
    
    return render(request, 'projets/modifier_projet.html', {
        'projet': projet,
        'realisations': realisations_disponibles,
    })


@login_required
def gerer_invitations(request, model, id):
    from communaute.models import Invitation
    
    projet = get_object_or_404(Projet, id=id)
    
    if projet.auteur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à gérer les invitations de ce projet.")
        return redirect('projets:detail_projet', id=id)
    
    invitations = Invitation.objects.filter(projet=projet).order_by('-date_creation')
    
    return render(request, 'projets/gerer_invitations.html', {
        'projet': projet,
        'invitations': invitations,
    })
