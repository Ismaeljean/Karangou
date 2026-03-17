from django.db import models
from django.db import models
from utilisateurs.models import Utilisateur
from realisations.models import Realisation


class Projet(models.Model):

    STATUS = (
        ('attente','En attente'),
        ('financement','En financement'),
        ('finance','Financé'),
        ('annule','Annulé')
    )

    titre = models.CharField(max_length=200)
    synopsis = models.TextField()
    pre_affiche = models.ImageField(upload_to="projets/pre_affiches/")
    budget_objectif = models.DecimalField(max_digits=12,decimal_places=2)
    montant_collecte = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    statut = models.CharField(max_length=20,choices=STATUS,default="attente")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    
    auteur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    realisation_source = models.OneToOneField(
        Realisation,
        on_delete=models.CASCADE
    )
    def __str__(self):

        return self.titre