from django.urls import path
from . import views

app_name = 'communaute'

urlpatterns = [
    path('forum/', views.forum, name='forum'),
    path('forum/<int:sujet_id>/', views.sujet_detail, name='sujet_detail'),
    path('forum/nouveau/', views.nouveau_sujet, name='nouveau_sujet'),
    path('films/<int:film_id>/commenter/', views.commenter_film, name='commenter_film'),
    path('films/<int:film_id>/noter/', views.noter_film, name='noter_film'),
]
