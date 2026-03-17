# karangou/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import View


class InactiveRedirectView(View):
    """Rediririge les utilisateurs vers la vérification OTP au lieu de la page inactivité"""
    def get(self, request):
        if request.session.get('pending_user_id'):
            return redirect('utilisateurs:verify_otp')
        return redirect('utilisateurs:login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('utilisateurs.urls')),
    path('', include('communaute.urls')),
    path('', include('financement.urls')),
    path('', include('projets.urls')),
    path('', include('realisations.urls')),
]

# Servez les fichiers statiques en mode débogage
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Servez les médias en mode débogage
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)