from django.urls import path
from . import views

app_name = 'projets'

urlpatterns = [
    path('projets/', views.liste_projets, name='liste_projets'),
    path('projets/<int:id>/', views.detail_projet, name='detail_projet'),
    path('projets/ajouter/', views.ajouter_projet, name='ajouter_projet'),
]
