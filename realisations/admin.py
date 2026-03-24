from django.contrib import admin
from django.utils.html import format_html
from .models import Realisation


@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'genre', 'duree', 'validation_badge', 'est_publie_badge', 'projet_lie', 'date_creation')
    list_filter = ('est_publie', 'est_soumis', 'est_brouillon', 'genre', 'annee_production', 'date_creation')
    search_fields = ('titre', 'pitch', 'synopsis', 'realisateur', 'auteur__nom', 'auteur__email')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Titre et Pitch', {
            'fields': ('titre', 'pitch', 'affiche')
        }),
        ('Médias', {
            'fields': ('bande_annonce', 'video')
        }),
        ('Fiche technique', {
            'fields': ('genre', 'duree', 'realisateur', 'pays', 'annee_production', 'langue_originale', 'casting', 'scenario', 'musique')
        }),
        ('Synopsis', {
            'fields': ('synopsis',)
        }),
        ('Informations', {
            'fields': ('auteur', 'date_sortie')
        }),
        ('Validation', {
            'fields': ('est_brouillon', 'est_soumis', 'message_admin')
        }),
        ('Publication', {
            'fields': ('est_publie', 'utilise_pour_financement', 'est_actif')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
    
    actions = ['valider_realisations', 'rejeter_realisations']
    
    def projet_lie(self, obj):
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        try:
            projet = obj.projet_financement
            url = reverse('admin:projets_projet_change', args=[projet.id])
            return format_html(
                '<a href="{}" target="_blank"><span style="background-color: #ff6b35; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span></a>',
                url,
                projet.titre[:20] + '...' if len(projet.titre) > 20 else projet.titre
            )
        except:
            return mark_safe('<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem;">Aucun</span>')
    projet_lie.short_description = 'Projet lié'
    
    def est_publie_badge(self, obj):
        color = '#28a745' if obj.est_publie else '#dc3545'
        label = 'Publié' if obj.est_publie else 'Non publié'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    est_publie_badge.short_description = 'Publié'
    
    def validation_badge(self, obj):
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
    
    def valider_realisations(self, request, queryset):
        count = queryset.filter(est_soumis=True).update(
            est_publie=True,
            est_soumis=False
        )
        self.message_user(request, f"{count} réalisation(s) publiée(s) avec succès.")
    valider_realisations.short_description = "Valider les réalisations sélectionnées (publier)"
    
    def rejeter_realisations(self, request, queryset):
        count = queryset.filter(est_soumis=True).count()
        queryset.filter(est_soumis=True).update(
            est_brouillon=True,
            est_soumis=False,
            message_admin='Réalisation refusée par l\'administrateur.'
        )
        self.message_user(request, f"{count} réalisation(s) rejetée(s).")
    rejeter_realisations.short_description = "Rejeter les réalisations sélectionnées"
