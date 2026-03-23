from django import template

register = template.Library()


@register.filter
def can_publish(user):
    """Vérifie si l'utilisateur peut publier des films/projets"""
    if user.role == 'auteur':
        return True
    if user.role == 'producteur' and user.is_verified:
        return True
    return False


@register.filter
def is_pending_producer(user):
    """Vérifie si l'utilisateur est un producteur en attente de validation"""
    if user.role == 'producteur' and not user.is_verified:
        return True
    return False


@register.inclusion_tag('utilisateurs/snippets/verification_alert.html')
def verification_alert(user):
    """Affiche une alerte si l'utilisateur est en attente de vérification"""
    return {'user': user}
