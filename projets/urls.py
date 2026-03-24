from django.urls import path
from . import views

app_name = 'projets'

urlpatterns = [
    path('projets/', views.liste_projets, name='liste_projets'),
    path('projets/<int:id>/', views.detail_projet, name='detail_projet'),
    path('projets/ajouter/', views.ajouter_projet, name='ajouter_projet'),
    path('projets/modifier/<int:id>/', views.modifier_projet, name='modifier_projet'),
    path('projets/soumettre/<int:id>/', views.soumettre_projet, name='soumettre_projet'),
    path('projets/mes/', views.mes_projets, name='mes_projets'),
    path('projets/gerer/invitations/<str:model>/<int:id>/', views.gerer_invitations, name='gerer_invitations'),
]
