from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Utilisateur, OtpCode, DocumentProfessionnel


@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = ('email', 'nom', 'prenom', 'role', 'is_verified', 'is_active', 'is_staff', 'date_creation')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'date_creation')
    search_fields = ('email', 'nom', 'prenom', 'numero')
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom', 'numero', 'role', 'bio', 'photo')}),
        ('Vérification', {'fields': ('is_verified',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'date_creation')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'password1', 'password2', 'role'),
        }),
    )
    
    actions = ['verifier_producteurs', 'desactiver_verification']

    def verifier_producteurs(self, request, queryset):
        for user in queryset.filter(role='producteur'):
            user.is_verified = True
            user.save()
        self.message_user(request, f"{queryset.filter(role='producteur').count()} producteur(s) vérifié(s).")
    verifier_producteurs.short_description = "Vérifier les producteurs sélectionnés"

    def desactiver_verification(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"Vérification désactivée pour {queryset.count()} utilisateur(s).")
    desactiver_verification.short_description = "Désactiver la vérification"


@admin.register(DocumentProfessionnel)
class DocumentProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'matricule_ministere', 'statut_badge', 'type_piece', 'date_soumission', 'actions_buttons')
    list_filter = ('statut', 'type_piece_identite', 'date_soumission')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'utilisateur__prenom', 'matricule_ministere')
    readonly_fields = ('utilisateur', 'matricule_ministere', 'type_piece_identite', 
                       'document_cni_passport', 'document_registre_commerce', 'document_rib',
                       'date_soumission')
    ordering = ('-date_soumission',)
    date_hierarchy = 'date_soumission'
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('utilisateur',)
        }),
        ('Informations professionnelles', {
            'fields': ('matricule_ministere', 'type_piece_identite')
        }),
        ('Documents', {
            'fields': ('document_cni_passport', 'document_registre_commerce', 'document_rib')
        }),
        ('Statut et validation', {
            'fields': ('statut', 'commentaire_admin', 'date_verification')
        }),
    )
    
    actions = ['approuver_documents', 'rejeter_documents']
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ffc107',
            'approuve': '#28a745',
            'rejete': '#dc3545'
        }
        labels = {
            'en_attente': 'En attente',
            'approuve': 'Approuvé',
            'rejete': 'Rejeté'
        }
        color = colors.get(obj.statut, '#6c757d')
        label = labels.get(obj.statut, obj.statut)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            color, label
        )
    statut_badge.short_description = 'Statut'
    
    def type_piece(self, obj):
        return dict(DocumentProfessionnel.TYPE_DOCUMENT_CHOICES).get(obj.type_piece_identite, obj.type_piece_identite)
    type_piece.short_description = 'Pièce identité'
    
    def actions_buttons(self, obj):
        if obj.statut == 'en_attente':
            approve_url = f'/admin/utilisateurs/documentprofessionnel/{obj.id}/change/'
            return format_html(
                '<a class="btn btn-sm btn-success" href="{}"><i class="bi bi-check-circle"></i> Approuver</a>',
                approve_url
            )
        return '-'
    actions_buttons.short_description = 'Actions rapides'
    
    def approuver_documents(self, request, queryset):
        queryset = queryset.filter(statut='en_attente')
        for doc in queryset:
            doc.statut = 'approuve'
            doc.date_verification = timezone.now()
            doc.save()
            doc.utilisateur.is_verified = True
            doc.utilisateur.save()
        self.message_user(request, f"{queryset.count()} document(s) approuvé(s). Les utilisateurs ont été vérifiés.")
    approuver_documents.short_description = "Approuver les documents sélectionnés"
    
    def rejeter_documents(self, request, queryset):
        queryset = queryset.filter(statut='en_attente')
        count = queryset.count()
        for doc in queryset:
            doc.statut = 'rejete'
            doc.date_verification = timezone.now()
            doc.save()
        self.message_user(request, f"{count} document(s) rejeté(s).")
    rejeter_documents.short_description = "Rejeter les documents sélectionnés"
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.statut != 'en_attente':
            readonly.append('statut')
        return readonly


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_identifier', 'utilisateur', 'created_at', 'is_valid_display')
    list_filter = ('created_at',)
    search_fields = ('code', 'numero', 'utilisateur__email', 'utilisateur__nom', 'utilisateur__prenom')
    readonly_fields = ('created_at', 'is_valid_display')
    date_hierarchy = 'created_at'
    
    def get_identifier(self, obj):
        if obj.numero:
            return obj.numero
        elif obj.utilisateur:
            return obj.utilisateur.email or obj.utilisateur.numero
        return "N/A"
    get_identifier.short_description = 'Identifiant'
    
    def is_valid_display(self, obj):
        is_valid = obj.is_valid()
        color = 'green' if is_valid else 'red'
        text = 'Valide' if is_valid else 'Expiré'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    is_valid_display.short_description = 'Statut'
