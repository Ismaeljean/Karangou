from django.urls import path
from . import views

app_name = 'communaute'

urlpatterns = [
    path('forum/', views.forum, name='forum'),
    path('forum/sujet/<int:sujet_id>/', views.sujet_detail, name='sujet_detail'),
    path('forum/nouveau/', views.nouveau_sujet, name='nouveau_sujet'),
    path('forum/sujet/<int:sujet_id>/commenter/', views.commenter_forum, name='commenter_forum'),
    
    path('films/<int:film_id>/commenter/', views.commenter_film, name='commenter_film'),
    path('films/<int:film_id>/noter/', views.noter_film, name='noter_film'),
    
    path('projets/<int:projet_id>/commenter/', views.commenter_projet, name='commenter_projet'),
    
    path('invitation/creer/<str:model_type>/<int:model_id>/<str:type_invitation>/', views.creer_invitation, name='creer_invitation'),
    path('invitations/', views.mes_invitations, name='mes_invitations'),
    path('invitation/<str:code>/', views.lien_invitation, name='lien_invitation'),
    path('invitation/accepter/<str:code>/', views.accepter_invitation, name='accepter_invitation'),
    path('invitation/revoquer/<str:code>/', views.revoquer_invitation, name='revoquer_invitation'),
]
