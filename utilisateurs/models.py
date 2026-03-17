# utilisateurs/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import datetime

# Gestionnaire de l'utilisateur
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(email, password, **extra_fields)



# Modèle pour l'utilisateur
class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('auteur','Auteur'),
        ('acteur','Acteur'),
        ('producteur','Producteur'),
        ('fan','Fan'),
    )

    # Username gardé pour compatibilité Django
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.CharField(max_length=15, blank=True, null=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='fan')
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profiles/",blank=True)
    is_verified = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# Modèle pour les codes OTP
class OtpCode(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    numero = models.CharField(max_length=20, blank=True, null=True)  # Peut être un numéro ou un email
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < datetime.timedelta(minutes=10)

    def __str__(self):
        identifier = self.numero or (self.utilisateur.numero if self.utilisateur else "N/A")
        return f"{identifier} - {self.code}"
