from django.contrib import admin
from .models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'budget_objectif', 'montant_collecte', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    search_fields = ('titre', 'synopsis', 'auteur__nom', 'auteur__email')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        ('Informations', {
            'fields': ('titre', 'synopsis', 'pre_affiche')
        }),
        ('Financement', {
            'fields': ('budget_objectif', 'montant_collecte', 'statut')
        }),
        ('Relations', {
            'fields': ('auteur', 'realisation_source')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
