from django.contrib import admin
from .models import Contribution


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'projet', 'montant', 'moyen_paiement', 'date_contribution')
    list_filter = ('moyen_paiement', 'date_contribution')
    search_fields = ('utilisateur__nom', 'utilisateur__email', 'projet__titre')
    date_hierarchy = 'date_contribution'
    readonly_fields = ('date_contribution',)
