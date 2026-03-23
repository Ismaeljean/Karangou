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

    def peut_publier(self):
        """Vérifie si l'utilisateur peut publier des films/projets"""
        if self.role == 'auteur':
            return True
        elif self.role == 'producteur':
            return self.is_verified
        return False

    def a_documents_approuves(self):
        """Vérifie si les documents du producteur sont approuvés"""
        if self.role != 'producteur':
            return True
        try:
            return self.documents_professionnels.statut == 'approuve'
        except:
            return False


# Modèle pour les documents professionnels des producteurs
class DocumentProfessionnel(models.Model):
    STATUT_CHOICES = (
        ('en_attente', 'En attente de vérification'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    )
    
    TYPE_DOCUMENT_CHOICES = (
        ('cni', 'CNI'),
        ('passport', 'Passeport'),
    )
    
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='documents_professionnels'
    )
    
    matricule_ministere = models.CharField(
        max_length=100,
        verbose_name="Matricule du Ministère de la Culture"
    )
    
    type_piece_identite = models.CharField(
        max_length=20,
        choices=TYPE_DOCUMENT_CHOICES,
        default='cni',
        verbose_name="Type de pièce d'identité"
    )
    
    document_cni_passport = models.FileField(
        upload_to="documents/cni_passport/",
        verbose_name="CNI ou Passeport",
        help_text="PDF ou image (max 7 Mo)"
    )
    
    document_registre_commerce = models.FileField(
        upload_to="documents/registre_commerce/",
        verbose_name="Registre de Commerce",
        help_text="PDF ou image (max 7 Mo)"
    )
    
    document_rib = models.FileField(
        upload_to="documents/rib/",
        verbose_name="RIB de l'entreprise",
        help_text="PDF ou image (max 7 Mo)"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_verification = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(
        blank=True,
        verbose_name="Commentaire de l'administrateur"
    )
    
    def __str__(self):
        return f"Documents de {self.utilisateur}"

    @property
    def est_approuve(self):
        return self.statut == 'approuve'


# Modèle pour les codes OTP
class OtpCode(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    numero = models.CharField(max_length=20, blank=True, null=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < datetime.timedelta(minutes=10)

    def __str__(self):
        identifier = self.numero or (self.utilisateur.numero if self.utilisateur else "N/A")
        return f"{identifier} - {self.code}"
