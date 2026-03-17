from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Utilisateur, OtpCode


@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    """Configuration admin pour le modèle Utilisateur"""
    list_display = ('email', 'nom', 'prenom', 'numero', 'role', 'is_active', 'is_staff', 'date_creation')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_creation')
    search_fields = ('email', 'nom', 'prenom', 'numero')
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom', 'numero', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'date_creation')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    """Configuration admin pour le modèle OtpCode"""
    list_display = ('code', 'get_identifier', 'utilisateur', 'created_at', 'is_valid_display')
    list_filter = ('created_at',)
    search_fields = ('code', 'numero', 'utilisateur__email', 'utilisateur__nom', 'utilisateur__prenom')
    readonly_fields = ('created_at', 'is_valid_display')
    date_hierarchy = 'created_at'
    
    def get_identifier(self, obj):
        """Affiche l'identifiant (email ou numéro)"""
        if obj.numero:
            return obj.numero
        elif obj.utilisateur:
            return obj.utilisateur.email or obj.utilisateur.numero
        return "N/A"
    get_identifier.short_description = 'Identifiant'
    
    def is_valid_display(self, obj):
        """Affiche si le code est valide avec une couleur"""
        is_valid = obj.is_valid()
        color = 'green' if is_valid else 'red'
        text = 'Valide' if is_valid else 'Expiré'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    is_valid_display.short_description = 'Statut'
