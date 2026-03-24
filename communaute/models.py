from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
import random
import string

from realisations.models import Realisation
from utilisateurs.models import Utilisateur


class Commentaire(models.Model):

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    film = models.ForeignKey(Realisation, on_delete=models.CASCADE, null=True, blank=True)
    projet = models.ForeignKey('projets.Projet', on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reponses')
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"Commentaire de {self.utilisateur} - {self.date.strftime('%d/%m/%Y')}"
    
    @property
    def est_produit_par_createur(self):
        if self.film:
            return self.utilisateur == self.film.auteur
        elif self.projet:
            return self.utilisateur == self.projet.auteur
        return False
    
    @property
    def est_auteur_invite(self):
        if self.film and self.film.auteurs_invites.filter(id=self.utilisateur.id).exists():
            return True
        if self.projet and self.projet.auteurs_invites.filter(id=self.utilisateur.id).exists():
            return True
        return False
    
    @property
    def est_acteur_invite(self):
        if self.film and self.film.acteurs_invites.filter(id=self.utilisateur.id).exists():
            return True
        if self.projet and self.projet.acteurs_invites.filter(id=self.utilisateur.id).exists():
            return True
        return False


class CommentaireForum(models.Model):

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    sujet = models.ForeignKey('SujetDuForum', on_delete=models.CASCADE, related_name='commentaires')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reponses')
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"Commentaire de {self.utilisateur} sur {self.sujet.titre}"


class Notation(models.Model):

    utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    film = models.ForeignKey(Realisation,on_delete=models.CASCADE)
    note = models.IntegerField()


class SujetDuForum(models.Model):

    auteur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)

    titre = models.CharField(max_length=200)

    contenu = models.TextField()

    date = models.DateTimeField(auto_now_add=True)


def generate_invitation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Invitation(models.Model):
    TYPE_CHOICES = (
        ('auteur', 'Auteur'),
        ('auteur_projet', 'Auteur (Projet)'),
        ('auteur_realisation', 'Auteur (Film)'),
        ('acteur', 'Acteur'),
    )
    
    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('expiree', 'Expirée'),
        ('revokee', 'Révoquée'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True, default=generate_invitation_code)
    type_invitation = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    projet = models.ForeignKey(
        'projets.Projet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='invitations_recues'
    )
    realisation = models.ForeignKey(
        Realisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='invitations_recues'
    )
    
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='invitations_envoyees'
    )
    email_invite = models.EmailField()
    invite = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations_recues'
    )
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_expiration = models.DateTimeField(null=True, blank=True)
    date_utilisation = models.DateTimeField(null=True, blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Invitation {self.code} - {self.type_invitation}"
    
    @property
    def est_expiree(self):
        return timezone.now() > self.date_expiration and self.statut == 'en_attente'
    
    @property
    def get_cible(self):
        if self.projet:
            return self.projet
        return self.realisation
    
    @property
    def get_cible_type(self):
        if self.projet:
            return 'projet'
        return 'realisation'
    
    def accepter(self, utilisateur):
        if self.statut != 'en_attente':
            return False
        if self.est_expiree:
            self.statut = 'expiree'
            self.save()
            return False
        
        self.invite = utilisateur
        self.statut = 'acceptee'
        self.date_utilisation = timezone.now()
        self.save()
        
        if self.type_invitation in ['auteur', 'auteur_projet'] and self.projet:
            self.projet.auteurs_invites.add(utilisateur)
        elif self.type_invitation == 'auteur_realisation' and self.realisation:
            self.realisation.auteurs_invites.add(utilisateur)
        elif self.type_invitation == 'acteur':
            if self.projet:
                self.projet.acteurs_invites.add(utilisateur)
            if self.realisation:
                self.realisation.acteurs_invites.add(utilisateur)
        
        return True