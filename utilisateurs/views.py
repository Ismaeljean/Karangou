from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count
from realisations.models import Realisation
from projets.models import Projet
from financement.models import Contribution
from utilisateurs.models import Utilisateur, OtpCode, DocumentProfessionnel
from communaute.models import Notation
import random
import string
from utilisateurs.utils.sendmail import send_otp_email




def index(request):
    films_recents = Realisation.objects.filter(est_publie=True, est_actif=True).order_by('-date_creation')[:6]
    projets_actifs = Projet.objects.filter(
        est_brouillon=False,
        est_soumis=True,
        statut__in=['financement', 'finance']
    ).order_by('-date_creation')[:4]
    
    # Stats dynamiques
    nb_films = Realisation.objects.filter(est_publie=True, est_actif=True).count()
    nb_projets_total = Projet.objects.count()
    nb_projets_financement = Projet.objects.filter(
        est_brouillon=False,
        est_soumis=True,
        statut__in=['financement', 'finance']
    ).count()
    nb_membres = Utilisateur.objects.count()
    
    # Satisfaction: pourcentage de notes positives (4 ou 5 étoiles)
    notations = Notation.objects.all()
    if notations.exists():
        notes_positives = notations.filter(note__gte=4).count()
        total_notes = notations.count()
        satisfaction = round((notes_positives / total_notes * 100)) if total_notes > 0 else 0
    else:
        satisfaction = 0
    
    return render(request, 'utilisateurs/index.html', {
        'films_recents': films_recents,
        'projets_actifs': projets_actifs,
        'nb_films': nb_films,
        'nb_projets_finances': nb_projets_financement,
        'nb_membres': nb_membres,
        'satisfaction': satisfaction,
    })


@login_required
def dashboard(request):
    user = request.user
    
    # Stats
    mes_realisations = Realisation.objects.filter(auteur=user).count()
    mes_projets = Projet.objects.filter(auteur=user).count()
    mes_contributions = Contribution.objects.filter(utilisateur=user).count()
    total_contribue = Contribution.objects.filter(utilisateur=user).aggregate(total=Sum('montant'))['total'] or 0
    
    # Recent
    recent_realisations = Realisation.objects.filter(auteur=user).order_by('-date_creation')[:3]
    recent_projets = Projet.objects.filter(auteur=user).order_by('-date_creation')[:3]
    recent_contributions = Contribution.objects.filter(utilisateur=user).order_by('-date_contribution')[:5]
    
    return render(request, 'utilisateurs/dashboard.html', {
        'mes_realisations': mes_realisations,
        'mes_projets': mes_projets,
        'mes_contributions': mes_contributions,
        'total_contribue': total_contribue,
        'recent_realisations': recent_realisations,
        'recent_projets': recent_projets,
        'recent_contributions': recent_contributions,
    })


@login_required
def complete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.nom = request.POST.get('nom', user.nom)
        user.prenom = request.POST.get('prenom', user.prenom)
        role = request.POST.get('role', 'fan')
        user.bio = request.POST.get('bio', '')
        
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
        
        if role == 'producteur':
            matricule = request.POST.get('matricule_ministere', '').strip()
            doc_cni = request.FILES.get('document_cni_passport')
            doc_registre = request.FILES.get('document_registre_commerce')
            doc_rib = request.FILES.get('document_rib')
            type_piece = request.POST.get('type_piece_identite', 'cni')
            
            errors = []
            if not matricule:
                errors.append("Le matricule du ministère est obligatoire.")
            if not doc_cni:
                errors.append("Le document CNI/Passeport est obligatoire.")
            if not doc_registre:
                errors.append("Le registre de commerce est obligatoire.")
            if not doc_rib:
                errors.append("Le RIB est obligatoire.")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'utilisateurs/complete_profile.html')
            
            user.role = role
            user.save()
            
            DocumentProfessionnel.objects.create(
                utilisateur=user,
                matricule_ministere=matricule,
                type_piece_identite=type_piece,
                document_cni_passport=doc_cni,
                document_registre_commerce=doc_registre,
                document_rib=doc_rib,
                statut='en_attente'
            )
            
            messages.success(request, "Votre profil a été enregistré. Vos documents seront vérifiés par un administrateur. Vous recevrez une notification une fois votre compte validé.")
        else:
            user.role = role
            user.is_verified = True
            user.save()
            messages.success(request, "Profil complété avec succès!")
        
        return redirect('utilisateurs:profile')
    
    if request.user.role and request.user.role != 'fan' or (request.user.nom and request.user.prenom):
        return redirect('utilisateurs:profile')
    
    return render(request, 'utilisateurs/complete_profile.html')


@login_required
def profile(request):
    return render(request, 'utilisateurs/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.nom = request.POST.get('nom', user.nom)
        user.prenom = request.POST.get('prenom', user.prenom)
        user.bio = request.POST.get('bio', user.bio)
        # Le rôle ne peut pas être modifié après l'inscription
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
        user.save()
        messages.success(request, "Profil mis à jour avec succès!")
        return redirect('utilisateurs:profile')
    return render(request, 'utilisateurs/edit_profile.html')


@login_required
def mes_realisations(request):
    from realisations.views import mes_realisations as realisations_mes
    return realisations_mes(request)


@login_required
def mes_projets(request):
    from projets.views import mes_projets as projets_mes
    return projets_mes(request)


def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)





#
def login_view(request):
    # Si there's pending OTP in session, redirect to verify-otp
    if request.session.get('pending_user_id') and request.session.get('otp_email'):
        return redirect('utilisateurs:verify_otp')
    
    if request.user.is_authenticated:
        return redirect('/')
    
    # Traiter la connexion
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    
    return render(request, 'account/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    # Traiter l'inscription
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        # nom/prenom are collected later in complete_profile
        nom = ''
        prenom = ''
        
        # Vérifications (nom/prenom sont demandés après vérification OTP)
        if not all([email, password, password2]):
            messages.error(request, "Tous les champs requis doivent être remplis.")
            return render(request, 'account/signup.html')
        
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'account/signup.html')
        
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au minimum 8 caractères.")
            return render(request, 'account/signup.html')
        
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'account/signup.html')
        
        # Créer l'utilisateur
        user = Utilisateur.objects.create_user(
            email=email,
            password=password,
            nom=nom,
            prenom=prenom,
            is_active=True,
            is_verified=False
        )
        
        # Générer le code OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        OtpCode.objects.create(
            utilisateur=user,
            numero=user.email,
            code=otp_code
        )
        
        # Envoyer l'email avec le code OTP
        send_otp_email(user.email, otp_code)
        
        # Stocker en session pour la vérification
        request.session['pending_user_id'] = user.id
        request.session['otp_email'] = user.email
        
        messages.success(request, f"Un code de vérification a été envoyé à {user.email}")
        return redirect('utilisateurs:verify_otp')
    
    return render(request, 'account/signup.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('/')


def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    pending_user_id = request.session.get('pending_user_id')
    otp_email = request.session.get('otp_email')
    
    if not pending_user_id or not otp_email:
        messages.error(request, "Session expirée. Veuillez vous inscrire à nouveau.")
        return redirect('utilisateurs:signup')
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        
        otp = OtpCode.objects.filter(
            utilisateur_id=pending_user_id,
            numero=otp_email,
            code=code
        ).first()
        
        if otp and otp.is_valid():
            from utilisateurs.models import Utilisateur
            try:
                user = Utilisateur.objects.get(id=pending_user_id)
                # Marquer l'utilisateur comme vérifié
                user.is_verified = True
                user.save()
                
                # Connecter l'utilisateur (utiliser notre backend email)
                login(request, user, backend='karangou.backends.EmailBackend')
                
                # Nettoyer la session en évitant KeyError si la clé a déjà été supprimée
                request.session.pop('pending_user_id', None)
                request.session.pop('otp_email', None)
                otp.delete()
                
                messages.success(request, "Compte vérifié avec succès!")
                
                return redirect('utilisateurs:complete_profile')
            except Utilisateur.DoesNotExist:
                messages.error(request, "Utilisateur non trouvé.")
        else:
            messages.error(request, "Code invalide ou expiré.")
    
    return render(request, 'utilisateurs/verify_otp.html', {'email': otp_email})

def resend_otp(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    pending_user_id = request.session.get('pending_user_id')
    otp_email = request.session.get('otp_email')
    
    if not pending_user_id or not otp_email:
        messages.error(request, "Session expirée. Veuillez vous inscrire à nouveau.")
        return redirect('utilisateurs:signup')
    
    from utilisateurs.models import Utilisateur
    try:
        user = Utilisateur.objects.get(id=pending_user_id)
        
        otp_code = ''.join(random.choices(string.digits, k=6))
        OtpCode.objects.create(
            utilisateur=user,
            numero=otp_email,
            code=otp_code
        )
        
        send_otp_email(otp_email, otp_code)
        messages.success(request, "Nouveau code envoyé!")
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé.")
    
    return redirect('utilisateurs:verify_otp')
