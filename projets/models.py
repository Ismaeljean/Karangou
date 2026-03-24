from django.db import models
from utilisateurs.models import Utilisateur
from realisations.models import Realisation


class Projet(models.Model):

    STATUS = (
        ('attente', 'En attente'),
        ('financement', 'En financement'),
        ('finance', 'Financé'),
        ('annule', 'Annulé')
    )

    GENRE_CHOICES = (
        ('action', 'Action'),
        ('drame', 'Drame'),
        ('comedie', 'Comédie'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('science-fiction', 'Science-Fiction'),
        ('documentaire', 'Documentaire'),
        ('animation', 'Animation'),
        ('aventure', 'Aventure'),
        ('horreur', 'Horreur'),
    )

    titre = models.CharField(max_length=200)
    synopsis = models.TextField(
        verbose_name="Synopsis",
        help_text="Résumé court du projet"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description complète",
        help_text="Description détaillée du projet"
    )
    genre = models.CharField(
        max_length=50,
        choices=GENRE_CHOICES,
        blank=True,
        verbose_name="Genre"
    )
    pre_affiche = models.ImageField(
        upload_to="projets/pre_affiches/",
        verbose_name="Pré-affiche"
    )
    budget_objectif = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    montant_collecte = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUS,
        default="attente"
    )
    date_debut = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de début du financement"
    )
    date_fin = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de fin du financement"
    )
    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='projets'
    )
    realisation_source = models.OneToOneField(
        Realisation,
        on_delete=models.CASCADE,
        related_name='projet_financement'
    )
    est_brouillon = models.BooleanField(default=True, verbose_name="Brouillon")
    est_soumis = models.BooleanField(default=False, verbose_name="Soumis pour validation")
    message_admin = models.TextField(blank=True, verbose_name="Message de l'administrateur")
    nom_banque = models.CharField(max_length=200, blank=True, verbose_name="Nom de la banque")
    numero_compte = models.CharField(max_length=50, blank=True, verbose_name="Numéro de compte")
    titulaire_compte = models.CharField(max_length=200, blank=True, verbose_name="Titulaire du compte")
    rib_document = models.FileField(upload_to="projets/ribs/", blank=True, null=True, verbose_name="Relevé d'identité bancaire (RIB)")
    
    auteurs_invites = models.ManyToManyField(
        'utilisateurs.Utilisateur',
        related_name='projets_collab',
        blank=True,
        verbose_name="Auteurs invités"
    )
    acteurs_invites = models.ManyToManyField(
        'utilisateurs.Utilisateur',
        related_name='projets_acteur',
        blank=True,
        verbose_name="Acteurs invités"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    @property
    def pourcentage(self):
        if self.budget_objectif > 0:
            return (self.montant_collecte / self.budget_objectif) * 100
        return 0

    @property
    def est_expire(self):
        if self.date_fin:
            from django.utils import timezone
            return timezone.now().date() > self.date_fin
        return False

    @property
    def jours_restants(self):
        if self.date_fin:
            from django.utils import timezone
            delta = self.date_fin - timezone.now().date()
            return max(0, delta.days)
        return None

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']
