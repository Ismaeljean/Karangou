from django.urls import path
from . import views

app_name = 'financement'

urlpatterns = [
    path('contribuer/<int:projet_id>/', views.contribuer, name='contribuer'),
    path('mes-contributions/', views.mes_contributions, name='mes_contributions'),
]
