from django.db import models
from utilisateurs.models import Utilisateur


class Realisation(models.Model):

    titre = models.CharField(max_length=255)
    pitch = models.CharField(
        max_length=500, 
        blank=True,
        verbose_name="Pitch / Accroche",
        help_text="Courte description pour attirer l'attention (max 500 caractères)"
    )
    
    affiche = models.ImageField(
        upload_to="realisations/affiches/",
        verbose_name="Affiche du film"
    )
    
    bande_annonce = models.FileField(
        upload_to="realisations/bandes_annonces/",
        blank=True,
        null=True,
        verbose_name="Bande-annonce",
        help_text="Video trailer (MP4, max 100 Mo)"
    )
    
    video = models.FileField(
        upload_to="realisations/videos/",
        blank=True,
        null=True,
        verbose_name="Film complet"
    )
    
    genre = models.CharField(max_length=100)
    duree = models.IntegerField(verbose_name="Durée (minutes)")
    
    realisateur = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Réalisateur"
    )
    
    pays = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Pays de production"
    )
    
    annee_production = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Année de production"
    )
    
    langue_originale = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Langue originale"
    )
    
    casting = models.TextField(
        blank=True,
        verbose_name="Casting / Acteurs",
        help_text="Liste des acteurs principaux"
    )
    
    scenario = models.TextField(
        blank=True,
        verbose_name="Scénario / Scénographie"
    )
    
    musique = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Musique / Compositeur"
    )
    
    synopsis = models.TextField(
        blank=True,
        verbose_name="Synopsis"
    )
    
    auteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE,
        related_name='realisations'
    )
    
    date_sortie = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de sortie"
    )
    
    est_publie = models.BooleanField(default=False)
    est_brouillon = models.BooleanField(default=True, verbose_name="Brouillon")
    est_soumis = models.BooleanField(default=False, verbose_name="Soumis pour validation")
    message_admin = models.TextField(blank=True, verbose_name="Message de l'administrateur")
    utilise_pour_financement = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=True)
    
    auteurs_invites = models.ManyToManyField(
        'utilisateurs.Utilisateur',
        related_name='realisations_collab',
        blank=True,
        verbose_name="Auteurs invités"
    )
    acteurs_invites = models.ManyToManyField(
        'utilisateurs.Utilisateur',
        related_name='realisations_acteur',
        blank=True,
        verbose_name="Acteurs invités"
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Réalisation"
        verbose_name_plural = "Réalisations"
        ordering = ['-date_creation']
