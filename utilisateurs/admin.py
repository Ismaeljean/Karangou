from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
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
    list_display = ('utilisateur', 'matricule_ministere', 'statut_badge', 'type_piece', 'date_soumission', 'actions_rapides')
    list_filter = ('statut', 'type_piece_identite', 'date_soumission')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'utilisateur__prenom', 'matricule_ministere')
    readonly_fields = ('utilisateur', 'matricule_ministere', 'type_piece_identite', 
                       'document_cni_passport', 'document_registre_commerce',
                       'date_soumission')
    ordering = ('-date_soumission',)
    date_hierarchy = 'date_soumission'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/validation/',
                self.admin_site.admin_view(self.page_validation_view),
                name='utilisateurs_documentprofessionnel_validation',
            ),
            path(
                '<path:object_id>/approuver/',
                self.admin_site.admin_view(self.approuver_producteur_view),
                name='utilisateurs_documentprofessionnel_approuver',
            ),
            path(
                '<path:object_id>/rejeter/',
                self.admin_site.admin_view(self.rejeter_producteur_view),
                name='utilisateurs_documentprofessionnel_rejeter',
            ),
        ]
        return custom_urls + urls
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('utilisateur',)
        }),
        ('Informations professionnelles', {
            'fields': ('matricule_ministere', 'type_piece_identite')
        }),
        ('Documents', {
            'fields': ('document_cni_passport', 'document_registre_commerce')
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
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    statut_badge.short_description = 'Statut'
    
    def type_piece(self, obj):
        return dict(DocumentProfessionnel.TYPE_DOCUMENT_CHOICES).get(obj.type_piece_identite, obj.type_piece_identite)
    type_piece.short_description = 'Pièce identité'
    
    def actions_rapides(self, obj):
        from django.urls import reverse
        validation_url = reverse('admin:utilisateurs_documentprofessionnel_validation', args=[obj.id])
        approuver_url = reverse('admin:utilisateurs_documentprofessionnel_approuver', args=[obj.id])
        rejeter_url = reverse('admin:utilisateurs_documentprofessionnel_rejeter', args=[obj.id])
        
        if obj.statut == 'en_attente':
            return format_html(
                '<div style="display: flex; flex-direction: column; gap: 4px;">'
                '<a href="{}" target="_blank" class="btn btn-sm btn-primary">📋 Voir</a>'
                '<a href="{}" class="btn btn-sm btn-success">✅ Approuver</a>'
                '<a href="{}" class="btn btn-sm btn-danger">❌ Rejeter</a>'
                '</div>',
                validation_url,
                approuver_url,
                rejeter_url
            )
        return mark_safe('<span style="color: #6c757d;">-</span>')
    actions_rapides.short_description = 'Actions'
    
    def page_validation_view(self, request, object_id):
        doc = self.get_object(request, object_id)
        if not doc:
            messages.error(request, "Document non trouvé.")
            return redirect('admin:utilisateurs_documentprofessionnel_changelist')
        
        utilisateur = doc.utilisateur
        can_validate = doc.statut == 'en_attente'
        
        context = {
            'title': f'Validation: {utilisateur.nom} {utilisateur.prenom}',
            'document': doc,
            'utilisateur': utilisateur,
            'can_validate': can_validate,
            'is_popup': False,
            'show_popup': False,
            'has_permission': True,
            'opts': self.model._meta,
            'preserved_filters': '',
        }
        return render(request, 'admin/utilisateurs/documentprofessionnel/validation.html', context)
    
    def approuver_producteur_view(self, request, object_id):
        doc = self.get_object(request, object_id)
        if not doc:
            messages.error(request, "Document non trouvé.")
            return redirect('admin:utilisateurs_documentprofessionnel_changelist')
        
        if doc.statut != 'en_attente':
            messages.warning(request, "Ce document ne peut pas être approuvé.")
            return redirect('admin:utilisateurs_documentprofessionnel_change', object_id)
        
        utilisateur = doc.utilisateur
        
        doc.statut = 'approuve'
        doc.date_verification = timezone.now()
        doc.save()
        
        utilisateur.is_verified = True
        utilisateur.save()
        
        messages.success(request, f"Producteur '{utilisateur.nom} {utilisateur.prenom}' approuvé avec succès!")
        return redirect('admin:utilisateurs_documentprofessionnel_changelist')
    
    def rejeter_producteur_view(self, request, object_id):
        if request.method == 'POST':
            doc = self.get_object(request, object_id)
            if not doc:
                messages.error(request, "Document non trouvé.")
                return redirect('admin:utilisateurs_documentprofessionnel_changelist')
            
            commentaire = request.POST.get('commentaire_admin', 'Documents rejetés par l\'administrateur.')
            
            doc.statut = 'rejete'
            doc.date_verification = timezone.now()
            doc.commentaire_admin = commentaire
            doc.save()
            
            messages.warning(request, f"Documents de '{doc.utilisateur.nom} {doc.utilisateur.prenom}' rejetés.")
            return redirect('admin:utilisateurs_documentprofessionnel_changelist')
        
        doc = self.get_object(request, object_id)
        if not doc:
            messages.error(request, "Document non trouvé.")
            return redirect('admin:utilisateurs_documentprofessionnel_changelist')
        
        context = {
            'title': f'Rejeter: {doc.utilisateur.nom} {doc.utilisateur.prenom}',
            'document': doc,
            'utilisateur': doc.utilisateur,
            'is_popup': False,
            'show_popup': False,
            'has_permission': True,
            'opts': self.model._meta,
            'preserved_filters': '',
        }
        return render(request, 'admin/utilisateurs/documentprofessionnel/rejet.html', context)
    
    def approuver_documents(self, request, queryset):
        queryset = queryset.filter(statut='en_attente')
        count = 0
        for doc in queryset:
            doc.statut = 'approuve'
            doc.date_verification = timezone.now()
            doc.save()
            doc.utilisateur.is_verified = True
            doc.utilisateur.save()
            count += 1
        self.message_user(request, f"{count} document(s) approuvé(s). Les utilisateurs ont été vérifiés.")
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
        color = '#28a745' if is_valid else '#dc3545'
        text = 'Valide' if is_valid else 'Expiré'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, text
        )
    is_valid_display.short_description = 'Statut'
