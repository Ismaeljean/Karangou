from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'lien_realisation', 'genre', 'budget_objectif', 'statut_badge', 'validation_badge', 'realisation_status', 'actions_rapides', 'date_creation')
    list_filter = ('statut', 'est_soumis', 'est_brouillon', 'genre', 'date_creation')
    search_fields = ('titre', 'synopsis', 'description', 'auteur__nom', 'auteur__email', 'realisation_source__titre')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification', 'pourcentage', 'est_expire', 'jours_restants')
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/valider/',
                self.admin_site.admin_view(self.valider_projet_view),
                name='projets_projet_valider',
            ),
            path(
                '<path:object_id>/rejeter/',
                self.admin_site.admin_view(self.rejeter_projet_view),
                name='projets_projet_rejeter',
            ),
            path(
                '<path:object_id>/validation/',
                self.admin_site.admin_view(self.page_validation_view),
                name='projets_projet_validation',
            ),
        ]
        return custom_urls + urls
    
    fieldsets = (
        ('Titre et synopsis', {
            'fields': ('titre', 'synopsis', 'description')
        }),
        ('Médias', {
            'fields': ('pre_affiche',)
        }),
        ('Classification', {
            'fields': ('genre',)
        }),
        ('Financement', {
            'fields': ('budget_objectif', 'montant_collecte', 'statut')
        }),
        ('Dates du financement', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Coordonnées bancaires', {
            'fields': ('nom_banque', 'numero_compte', 'titulaire_compte', 'rib_document')
        }),
        ('Relations', {
            'fields': ('auteur', 'realisation_source')
        }),
        ('Validation', {
            'fields': ('est_brouillon', 'est_soumis', 'message_admin')
        }),
        ('Statistiques', {
            'fields': ('pourcentage', 'est_expire', 'jours_restants'),
            'classes': ('collapse',)
        }),
        ('Dates système', {
            'fields': ('date_creation', 'date_modification')
        }),
    )
    
    actions = ['valider_avec_realisation', 'valider_projets', 'rejeter_projets']
    
    def lien_realisation(self, obj):
        from django.urls import reverse
        url = reverse('admin:projets_projet_validation', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" class="btn btn-sm btn-primary">📋 {}</a>',
            url,
            obj.realisation_source.titre
        )
    lien_realisation.short_description = 'Actions'
    
    def actions_rapides(self, obj):
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        valider_url = reverse('admin:projets_projet_valider', args=[obj.id])
        rejeter_url = reverse('admin:projets_projet_rejeter', args=[obj.id])
        
        if obj.est_soumis:
            return format_html(
                '<a href="{}" class="btn btn-sm btn-success" style="margin-right: 5px;">✅ Valider</a>'
                '<a href="{}" class="btn btn-sm btn-danger">❌ Rejeter</a>',
                valider_url,
                rejeter_url
            )
        return mark_safe('<span style="color: #6c757d;">-</span>')
    actions_rapides.short_description = 'Actions rapides'
    
    def realisation_status(self, obj):
        realisation = obj.realisation_source
        if realisation.est_publie:
            color = '#28a745'
            label = 'Publiée'
        elif realisation.est_soumis:
            color = '#ffc107'
            label = 'En attente'
        else:
            color = '#6c757d'
            label = 'Brouillon'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    realisation_status.short_description = 'Statut Réalisation'
    
    def pourcentage(self, obj):
        return f"{obj.pourcentage:.1f}%"
    pourcentage.short_description = 'Progression'
    
    def est_expire(self, obj):
        return obj.est_expire
    est_expire.short_description = 'Expiré'
    est_expire.boolean = True
    
    def jours_restants(self, obj):
        jours = obj.jours_restants
        return f"{jours} jour{'s' if jours and jours > 1 else ''}" if jours is not None else "N/A"
    jours_restants.short_description = 'Jours restants'
    
    def statut_badge(self, obj):
        colors = {
            'attente': '#ffc107',
            'financement': '#ff6b35',
            'finance': '#28a745',
            'annule': '#dc3545'
        }
        labels = {
            'attente': 'En attente',
            'financement': 'En financement',
            'finance': 'Financé',
            'annule': 'Annulé'
        }
        color = colors.get(obj.statut, '#6c757d')
        label = labels.get(obj.statut, obj.statut)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    statut_badge.short_description = 'Statut'
    
    def validation_badge(self, obj):
        if obj.est_brouillon:
            color = '#6c757d'
            label = 'Brouillon'
        elif obj.est_soumis:
            color = '#ffc107'
            label = 'En attente'
        else:
            color = '#28a745'
            label = 'Approuvé'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, label
        )
    validation_badge.short_description = 'Validation'
    
    def valider_avec_realisation(self, request, queryset):
        from realisations.models import Realisation
        count_projets = 0
        count_realisations = 0
        
        for projet in queryset.filter(est_soumis=True):
            realisation = projet.realisation_source
            
            if not realisation.est_publie and realisation.est_soumis:
                realisation.est_publie = True
                realisation.est_soumis = False
                realisation.save()
                count_realisations += 1
            
            projet.statut = 'financement'
            projet.est_soumis = False
            projet.save()
            count_projets += 1
        
        self.message_user(request, f"{count_projets} projet(s) validé(s) et {count_realisations} réalisation(s) publiée(s) avec succès!")
    valider_avec_realisation.short_description = "Valider projet ET réalisation ensemble"
    
    def valider_projets(self, request, queryset):
        count = queryset.filter(est_soumis=True).update(
            statut='financement',
            est_soumis=False
        )
        self.message_user(request, f"{count} projet(s) mis en financement avec succès.")
    valider_projets.short_description = "Valider les projets sélectionnés (sans la réalisation)"
    
    def rejeter_projets(self, request, queryset):
        count = queryset.filter(est_soumis=True).count()
        queryset.filter(est_soumis=True).update(
            est_brouillon=True,
            est_soumis=False,
            message_admin='Projet refusé par l\'administrateur.'
        )
        self.message_user(request, f"{count} projet(s) rejeté(s).")
    rejeter_projets.short_description = "Rejeter les projets sélectionnés"
    
    def page_validation_view(self, request, object_id):
        projet = self.get_object(request, object_id)
        if not projet:
            messages.error(request, "Projet non trouvé.")
            return redirect('admin:projets_projet_changelist')
        
        realisation = projet.realisation_source
        can_validate = projet.est_soumis and projet.statut == 'attente'
        
        context = {
            'title': f'Validation: {projet.titre}',
            'projet': projet,
            'realisation': realisation,
            'can_validate': can_validate,
            'is_popup': False,
            'show_popup': False,
            'has_permission': True,
            'opts': self.model._meta,
            'preserved_filters': '',
        }
        return render(request, 'admin/projets/projet/validation.html', context)
    
    def valider_projet_view(self, request, object_id):
        projet = self.get_object(request, object_id)
        if not projet:
            messages.error(request, "Projet non trouvé.")
            return redirect('admin:projets_projet_changelist')
        
        if not projet.est_soumis:
            messages.warning(request, "Ce projet ne peut pas être validé.")
            return redirect('admin:projets_projet_change', object_id)
        
        realisation = projet.realisation_source
        realisation.est_publie = True
        realisation.est_soumis = False
        realisation.save()
        
        projet.statut = 'financement'
        projet.est_soumis = False
        projet.save()
        
        messages.success(request, f"Projet '{projet.titre}' validé et réalisation '{realisation.titre}' publiée avec succès!")
        return redirect('admin:projets_projet_changelist')
    
    def rejeter_projet_view(self, request, object_id):
        if request.method == 'POST':
            projet = self.get_object(request, object_id)
            if not projet:
                messages.error(request, "Projet non trouvé.")
                return redirect('admin:projets_projet_changelist')
            
            message = request.POST.get('message_admin', 'Projet refusé par l\'administrateur.')
            
            projet.est_brouillon = True
            projet.est_soumis = False
            projet.message_admin = message
            projet.save()
            
            messages.warning(request, f"Projet '{projet.titre}' rejeté.")
            return redirect('admin:projets_projet_changelist')
        
        projet = self.get_object(request, object_id)
        if not projet:
            messages.error(request, "Projet non trouvé.")
            return redirect('admin:projets_projet_changelist')
        
        context = {
            'title': f'Rejeter: {projet.titre}',
            'projet': projet,
            'is_popup': False,
            'show_popup': False,
            'has_permission': True,
            'opts': self.model._meta,
            'preserved_filters': '',
        }
        return render(request, 'admin/projets/projet/rejet.html', context)
