from django.urls import path
from . import views

app_name = 'realisations'

urlpatterns = [
    path('', views.index, name='index'),
    path('films/', views.liste_films, name='liste_films'),
    path('films/<int:id>/', views.detail_film, name='detail_film'),
    path('films/ajouter/', views.ajouter_realisation, name='ajouter_realisation'),
    path('films/modifier/<int:id>/', views.modifier_realisation, name='modifier_realisation'),
    path('films/soumettre/<int:id>/', views.soumettre_realisation, name='soumettre_realisation'),
    path('mes-realisations/', views.mes_realisations, name='mes_realisations'),
]
