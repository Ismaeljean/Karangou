from django.contrib import admin
from .models import Commentaire, Notation, SujetDuForum


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'film', 'contenu', 'date')
    list_filter = ('film', 'date')
    search_fields = ('utilisateur__nom', 'utilisateur__email', 'contenu')
    date_hierarchy = 'date'


@admin.register(Notation)
class NotationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'film', 'note')
    list_filter = ('film', 'note')
    search_fields = ('utilisateur__nom', 'utilisateur__email')


@admin.register(SujetDuForum)
class SujetDuForumAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date')
    list_filter = ('date',)
    search_fields = ('titre', 'contenu', 'auteur__nom', 'auteur__email')
    date_hierarchy = 'date'
