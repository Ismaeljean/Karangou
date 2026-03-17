from django.db import models
from utilisateurs.models import Utilisateur

class Realisation(models.Model):

    titre = models.CharField(max_length=255)
    description = models.TextField()
    affiche = models.ImageField(upload_to="realisations/affiches/")
    video = models.FileField(upload_to="realisations/videos/")
    genre = models.CharField(max_length=100)
    duree = models.IntegerField()
    auteur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    date_sortie = models.DateField()
    est_publie = models.BooleanField(default=False)
    utilise_pour_financement = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):

        return self.titre