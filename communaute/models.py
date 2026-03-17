from django.db import models

from realisations.models import Realisation
from utilisateurs.models import Utilisateur


class Commentaire(models.Model):

    utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    film = models.ForeignKey(Realisation,on_delete=models.CASCADE)
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Notation(models.Model):

    utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    film = models.ForeignKey(Realisation,on_delete=models.CASCADE)
    note = models.IntegerField()


class SujetDuForum(models.Model):

    auteur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)

    titre = models.CharField(max_length=200)

    contenu = models.TextField()

    date = models.DateTimeField(auto_now_add=True)