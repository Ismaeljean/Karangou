from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Commentaire, Notation, SujetDuForum
from realisations.models import Realisation

def forum(request):
    sujets = SujetDuForum.objects.all().order_by('-date')[:20]
    return render(request, 'communaute/forum.html', {
        'sujets': sujets
    })

def sujet_detail(request, sujet_id):
    sujet = get_object_or_404(SujetDuForum, id=sujet_id)
    return render(request, 'communaute/sujet_detail.html', {
        'sujet': sujet
    })

@login_required
def nouveau_sujet(request):
    if request.method == 'POST':
        sujet = SujetDuForum(
            auteur=request.user,
            titre=request.POST.get('titre'),
            contenu=request.POST.get('contenu'),
        )
        sujet.save()
        messages.success(request, "Sujet créé avec succès!")
        return redirect('communaute:sujet_detail', sujet_id=sujet.id)
    return render(request, 'communaute/nouveau_sujet.html')

@login_required
def commenter_film(request, film_id):
    film = get_object_or_404(Realisation, id=film_id)
    if request.method == 'POST':
        commentaire = Commentaire(
            utilisateur=request.user,
            film=film,
            contenu=request.POST.get('contenu'),
        )
        commentaire.save()
        messages.success(request, "Commentaire ajouté!")
    return redirect('realisations:detail_film', id=film_id)

@login_required
def noter_film(request, film_id):
    film = get_object_or_404(Realisation, id=film_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        try:
            note = int(note)
            if 1 <= note <= 5:
                Notation.objects.update_or_create(
                    utilisateur=request.user,
                    film=film,
                    defaults={'note': note}
                )
                messages.success(request, "Note enregistrée!")
        except ValueError:
            messages.error(request, "Note invalide.")
    return redirect('realisations:detail_film', id=film_id)
