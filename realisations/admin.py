from django.contrib import admin
from .models import Realisation


@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'genre', 'duree', 'est_publie', 'date_sortie', 'date_creation')
    list_filter = ('est_publie', 'genre', 'date_sortie', 'date_creation')
    search_fields = ('titre', 'description', 'auteur__nom', 'auteur__email')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        ('Informations', {
            'fields': ('titre', 'description', 'affiche', 'video')
        }),
        ('Détails', {
            'fields': ('genre', 'duree', 'date_sortie', 'auteur')
        }),
        ('Statut', {
            'fields': ('est_publie', 'utilise_pour_financement', 'est_actif')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
