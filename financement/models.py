from django.db import models

from django.db import models
from utilisateurs.models import Utilisateur
from projets.models import Projet

class Contribution(models.Model):

    utilisateur = models.ForeignKey(Utilisateur,on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet,on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10,decimal_places=2)
    date_contribution = models.DateTimeField(auto_now_add=True)
    moyen_paiement = models.CharField(max_length=50)



    def __str__(self):

        return f"{self.utilisateur} -> {self.projet}"