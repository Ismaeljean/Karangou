from django.contrib import admin
from django.utils import timezone
from .models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'genre', 'budget_objectif', 'statut_badge', 'validation_badge', 'date_creation')
    list_filter = ('statut', 'est_soumis', 'est_brouillon', 'genre', 'date_creation')
    search_fields = ('titre', 'synopsis', 'description', 'auteur__nom', 'auteur__email')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification', 'pourcentage', 'est_expire', 'jours_restants')
    
    fieldsets = (
        ('Titre et synopsis', {
            'fields': ('titre', 'synopsis', 'description')
        }),
        ('Médias', {
            'fields': ('pre_affiche',)
        }),
        ('Classification', {
            'fields': ('genre',)
        }),
        ('Financement', {
            'fields': ('budget_objectif', 'montant_collecte', 'statut')
        }),
        ('Dates du financement', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Relations', {
            'fields': ('auteur', 'realisation_source')
        }),
        ('Validation', {
            'fields': ('est_brouillon', 'est_soumis', 'message_admin')
        }),
        ('Statistiques', {
            'fields': ('pourcentage', 'est_expire', 'jours_restants'),
            'classes': ('collapse',)
        }),
        ('Dates système', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
    
    actions = ['valider_projets', 'rejeter_projets']
    
    def pourcentage(self, obj):
        return f"{obj.pourcentage:.1f}%"
    pourcentage.short_description = 'Progression'
    
    def est_expire(self, obj):
        return obj.est_expire
    est_expire.short_description = 'Expiré'
    est_expire.boolean = True
    
    def jours_restants(self, obj):
        jours = obj.jours_restants
        return f"{jours} jour{'s' if jours and jours > 1 else ''}" if jours is not None else "N/A"
    jours_restants.short_description = 'Jours restants'
    
    def statut_badge(self, obj):
        colors = {
            'attente': '#ffc107',
            'financement': '#ff6b35',
            'finance': '#28a745',
            'annule': '#dc3545'
        }
        labels = {
            'attente': 'En attente',
            'financement': 'En financement',
            'finance': 'Financé',
            'annule': 'Annulé'
        }
        color = colors.get(obj.statut, '#6c757d')
        label = labels.get(obj.statut, obj.statut)
        from django.utils.html import format_html
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    statut_badge.short_description = 'Statut'
    
    def validation_badge(self, obj):
        from django.utils.html import format_html
        if obj.est_brouillon:
            color = '#6c757d'
            label = 'Brouillon'
        elif obj.est_soumis:
            color = '#ffc107'
            label = 'En attente'
        else:
            color = '#28a745'
            label = 'Approuvé'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    validation_badge.short_description = 'Validation'
    
    def valider_projets(self, request, queryset):
        count = queryset.filter(est_soumis=True).update(
            statut='financement',
            est_soumis=False
        )
        self.message_user(request, f"{count} projet(s) mis en financement avec succès.")
    valider_projets.short_description = "Valider les projets sélectionnés (lancer le financement)"
    
    def rejeter_projets(self, request, queryset):
        count = queryset.filter(est_soumis=True).count()
        queryset.filter(est_soumis=True).update(
            est_brouillon=True,
            est_soumis=False,
            message_admin='Projet refusé par l\'administrateur.'
        )
        self.message_user(request, f"{count} projet(s) rejeté(s).")
    rejeter_projets.short_description = "Rejeter les projets sélectionnés"
