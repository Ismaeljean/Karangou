from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class VerifyOtpMixin:
    """Mixin qui ajoute la vérification OTP à n'importe quel backend"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Appeler la méthode parent
        user = super().authenticate(request, username, password, **kwargs)
        
        if user is not None:
            # Les superutilisateurs et staff peuvent se connecter sans vérification OTP
            if user.is_superuser or user.is_staff:
                return user
            
            # Pour les utilisateurs normaux, vérifier que l'utilisateur a vérifié son email OTP
            if hasattr(user, 'is_verified') and not user.is_verified:
                return None
        
        return user


class OtpVerifiedModelBackend(VerifyOtpMixin, ModelBackend):
    """Backend standard Django modifié pour vérifier OTP"""
    pass


class EmailBackend(VerifyOtpMixin, ModelBackend):
    """Backend qui accepte les connexions par email et vérifie l'OTP"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            User().set_password(password)
            return None
        
        # Utiliser le parent pour vérifier le password et OTP
        if user.check_password(password) and self.user_can_authenticate(user):
            # Les superutilisateurs et staff peuvent se connecter sans vérification OTP
            if user.is_superuser or user.is_staff:
                return user
            
            # Pour les utilisateurs normaux, vérifier que l'utilisateur a vérifié son email OTP
            if hasattr(user, 'is_verified') and not user.is_verified:
                return None
            return user
        return None



