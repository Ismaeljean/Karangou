from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Commentaire, Notation, SujetDuForum, Invitation, CommentaireForum
from realisations.models import Realisation
from projets.models import Projet


def forum(request):
    sujets = SujetDuForum.objects.all().order_by('-date')[:20]
    nb_commentaires_forum = CommentaireForum.objects.count()
    nb_participants = SujetDuForum.objects.values('auteur').distinct().count()
    sujets_populaires = SujetDuForum.objects.order_by('-date')[:5]
    return render(request, 'communaute/forum.html', {
        'sujets': sujets,
        'nb_commentaires': nb_commentaires_forum,
        'nb_participants': nb_participants,
        'sujets_populaires': sujets_populaires,
    })

def sujet_detail(request, sujet_id):
    sujet = get_object_or_404(SujetDuForum, id=sujet_id)
    commentaires = CommentaireForum.objects.filter(sujet=sujet, parent__isnull=True).order_by('date')
    return render(request, 'communaute/sujet_detail.html', {
        'sujet': sujet,
        'commentaires': commentaires,
    })

@login_required
def nouveau_sujet(request):
    if request.method == 'POST':
        sujet = SujetDuForum(
            auteur=request.user,
            titre=request.POST.get('titre'),
            contenu=request.POST.get('contenu'),
        )
        sujet.save()
        messages.success(request, "Sujet créé avec succès!")
        return redirect('communaute:sujet_detail', sujet_id=sujet.id)
    return render(request, 'communaute/nouveau_sujet.html')

@login_required
def commenter_film(request, film_id):
    film = get_object_or_404(Realisation, id=film_id)
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = Commentaire.objects.get(id=parent_id)
            except Commentaire.DoesNotExist:
                pass
        
        commentaire = Commentaire(
            utilisateur=request.user,
            film=film,
            parent=parent,
            contenu=request.POST.get('contenu'),
        )
        commentaire.save()
        
        if parent:
            messages.success(request, "Réponse ajoutée!")
        else:
            messages.success(request, "Commentaire ajouté!")
    return redirect('realisations:detail_film', id=film_id)

@login_required
def noter_film(request, film_id):
    film = get_object_or_404(Realisation, id=film_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        try:
            note = int(note)
            if 1 <= note <= 5:
                Notation.objects.update_or_create(
                    utilisateur=request.user,
                    film=film,
                    defaults={'note': note}
                )
                messages.success(request, "Note enregistrée!")
        except ValueError:
            messages.error(request, "Note invalide.")
    return redirect('realisations:detail_film', id=film_id)

@login_required
def commenter_projet(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = Commentaire.objects.get(id=parent_id)
            except Commentaire.DoesNotExist:
                pass
        
        commentaire = Commentaire(
            utilisateur=request.user,
            projet=projet,
            parent=parent,
            contenu=request.POST.get('contenu'),
        )
        commentaire.save()
        
        if parent:
            messages.success(request, "Réponse ajoutée!")
        else:
            messages.success(request, "Commentaire ajouté!")
    return redirect('projets:detail_projet', id=projet_id)

@login_required
def commenter_forum(request, sujet_id):
    sujet = get_object_or_404(SujetDuForum, id=sujet_id)
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = CommentaireForum.objects.get(id=parent_id)
            except CommentaireForum.DoesNotExist:
                pass
        
        commentaire = CommentaireForum(
            utilisateur=request.user,
            sujet=sujet,
            parent=parent,
            contenu=request.POST.get('contenu'),
        )
        commentaire.save()
        
        if parent:
            messages.success(request, "Réponse ajoutée!")
        else:
            messages.success(request, "Commentaire ajouté!")
    return redirect('communaute:sujet_detail', sujet_id=sujet_id)


@login_required
def creer_invitation(request, model_type, model_id, type_invitation):
    if request.user.role != 'producteur':
        messages.error(request, "Seuls les producteurs peuvent envoyer des invitations.")
        return redirect('utilisateurs:profile')
    
    if model_type == 'projet':
        try:
            projet = Projet.objects.get(id=model_id)
            if projet.auteur != request.user:
                messages.error(request, "Vous n'êtes pas autorisé à inviter sur ce projet.")
                return redirect('projets:detail_projet', id=model_id)
            cible = projet
            type_invitation_final = 'auteur_projet'
        except Projet.DoesNotExist:
            messages.error(request, "Projet non trouvé.")
            return redirect('utilisateurs:profile')
    elif model_type == 'realisation':
        try:
            realisation = Realisation.objects.get(id=model_id)
            if realisation.auteur != request.user:
                messages.error(request, "Vous n'êtes pas autorisé à inviter sur cette réalisation.")
                return redirect('realisations:detail_film', id=model_id)
            cible = realisation
            type_invitation_final = 'auteur_realisation'
        except Realisation.DoesNotExist:
            messages.error(request, "Réalisation non trouvée.")
            return redirect('utilisateurs:profile')
    else:
        messages.error(request, "Type invalide.")
        return redirect('utilisateurs:profile')
    
    if request.method == 'POST':
        email_invite = request.POST.get('email_invite', '').strip().lower()
        type_role = request.POST.get('type_invitation', 'auteur')
        
        if not email_invite:
            messages.error(request, "L'email est obligatoire.")
            return render(request, 'communaute/invitation_form.html', {
                'cible': cible,
                'model_type': model_type,
                'type_invitation': type_role,
            })
        
        type_invitation_final = f'auteur_{model_type}' if type_role == 'auteur' else 'acteur'
        
        invitations_existantes = Invitation.objects.filter(
            email_invite=email_invite,
            projet=projet if model_type == 'projet' else None,
            realisation=realisation if model_type == 'realisation' else None,
            statut__in=['en_attente', 'acceptee']
        )
        
        if invitations_existantes.exists():
            messages.warning(request, "Une invitation a déjà été envoyée à cet email pour ce contenu.")
            return render(request, 'communaute/invitation_form.html', {
                'cible': cible,
                'model_type': model_type,
                'type_invitation': type_role,
            })
        
        invitation = Invitation.objects.create(
            type_invitation=type_invitation_final,
            projet=projet if model_type == 'projet' else None,
            realisation=realisation if model_type == 'realisation' else None,
            createur=request.user,
            email_invite=email_invite,
            date_expiration=timezone.now() + timedelta(days=7),
        )
        
        lien_invitation = request.build_absolute_uri(f'/invitation/{invitation.code}/')
        
        try:
            send_invitation_email(
                email_invite,
                request.user,
                cible,
                type_role,
                invitation.code,
                lien_invitation
            )
            messages.success(request, f"Invitation envoyée à {email_invite}!")
        except Exception as e:
            messages.warning(request, f"Invitation créée mais l'envoi d'email a échoué. Code: {invitation.code}")
        
        if model_type == 'projet':
            return redirect('projets:gerer_invitations', 'projet', model_id)
        else:
            return redirect('realisations:gerer_invitations', 'realisation', model_id)
    
    return render(request, 'communaute/invitation_form.html', {
        'cible': cible,
        'model_type': model_type,
        'type_invitation': type_invitation,
    })


def lien_invitation(request, code):
    invitation = get_object_or_404(Invitation, code=code)
    
    if invitation.statut == 'acceptee':
        messages.info(request, "Cette invitation a déjà été acceptée.")
    elif invitation.statut == 'expiree':
        messages.warning(request, "Cette invitation a expiré.")
    elif invitation.statut == 'revokee':
        messages.warning(request, "Cette invitation a été révoquée.")
    
    return render(request, 'communaute/lien_invitation.html', {
        'invitation': invitation,
    })


@login_required
def accepter_invitation(request, code):
    invitation = get_object_or_404(Invitation, code=code)
    
    if invitation.invite and invitation.invite != request.user:
        messages.error(request, "Cette invitation a été acceptée par un autre utilisateur.")
        return redirect('utilisateurs:profile')
    
    if invitation.statut == 'acceptee':
        messages.info(request, "Vous avez déjà accepté cette invitation.")
        cible = invitation.projet or invitation.realisation
        if cible:
            if invitation.projet:
                return redirect('projets:detail_projet', id=invitation.projet.id)
            else:
                return redirect('realisations:detail_film', id=invitation.realisation.id)
        return redirect('utilisateurs:profile')
    
    if invitation.statut in ['expiree', 'revokee']:
        messages.error(request, "Cette invitation n'est plus disponible.")
        return redirect('communaute:lien_invitation', code=code)
    
    if request.user.email.lower() != invitation.email_invite.lower():
        messages.warning(request, f"Cette invitation a été envoyée à {invitation.email_invite}. Vous êtes connecté avec {request.user.email}.")
    
    if invitation.accepter(request.user):
        messages.success(request, "Invitation acceptée! Vous êtes maintenant associé à ce contenu.")
    else:
        messages.error(request, "Impossible d'accepter l'invitation.")
    
    cible = invitation.projet or invitation.realisation
    if cible:
        if invitation.projet:
            return redirect('projets:detail_projet', id=invitation.projet.id)
        else:
            return redirect('realisations:detail_film', id=invitation.realisation.id)
    return redirect('utilisateurs:profile')


@login_required
def mes_invitations(request):
    invitations = Invitation.objects.filter(
        email_invite=request.user.email.lower()
    ).order_by('-date_creation')
    
    invitations_actives = invitations.filter(statut='en_attente', date_expiration__gte=timezone.now())
    invitations_acceptees = invitations.filter(statut='acceptee')
    invitations_expirees = invitations.filter(statut__in=['expiree', 'revokee'])
    
    return render(request, 'communaute/mes_invitations.html', {
        'invitations_actives': invitations_actives,
        'invitations_acceptees': invitations_acceptees,
        'invitations_expirees': invitations_expirees,
    })


@login_required
def revoquer_invitation(request, code):
    invitation = get_object_or_404(Invitation, code=code)
    
    if invitation.createur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à révoquer cette invitation.")
        return redirect('utilisateurs:profile')
    
    if invitation.statut != 'en_attente':
        messages.warning(request, "Cette invitation ne peut pas être révoquée.")
        return redirect('utilisateurs:profile')
    
    invitation.statut = 'revokee'
    invitation.save()
    messages.success(request, "Invitation révoquée avec succès.")
    
    cible = invitation.projet or invitation.realisation
    if cible:
        if invitation.projet:
            return redirect('projets:gerer_invitations', 'projet', invitation.projet.id)
        else:
            return redirect('realisations:gerer_invitations', 'realisation', invitation.realisation.id)
    return redirect('utilisateurs:profile')


def send_invitation_email(email_invite, createur, cible, type_invitation, code, lien):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    if hasattr(cible, 'titre'):
        titre_cible = cible.titre
    else:
        titre_cible = str(cible)
    
    type_label = "Auteur" if type_invitation == 'auteur' else "Acteur"
    
    subject = f"Vous êtes invité à rejoindre '{titre_cible}' sur Karangou"
    
    message = f"""Bonjour,

{createur.get_full_name()} vous invite à rejoindre le{' projet' if hasattr(cible, 'budget_objectif') else ' film'} "{titre_cible}" en tant que {type_label} sur Karangou.

Code d'invitation: {code}

Cliquez ici pour accepter: {lien}

Ce lien expire dans 7 jours.

À bientôt sur Karangou!
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_invite],
            fail_silently=True,
        )
        return True
    except Exception:
        return False
