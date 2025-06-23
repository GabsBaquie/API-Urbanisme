from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Zone, Idea, Vote


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Administration des utilisateurs"""
    list_display = ['email', 'username', 'is_anonymous', 'is_active', 'date_joined']
    list_filter = ['is_anonymous', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('is_anonymous',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('is_anonymous',)}),
    )


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Administration des zones géographiques"""
    list_display = ['name', 'zone_type', 'latitude', 'longitude', 'idea_count', 'created_at']
    list_filter = ['zone_type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def idea_count(self, obj):
        return obj.ideas.count()
    idea_count.short_description = 'Nombre d\'idées'


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    """Administration des idées"""
    list_display = ['title', 'category', 'status', 'author', 'zone', 'vote_count', 'created_at']
    list_filter = ['category', 'status', 'created_at', 'zone']
    search_fields = ['title', 'description', 'author__email', 'zone__name']
    ordering = ['-created_at']
    readonly_fields = ['vote_count', 'positive_votes', 'negative_votes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'category', 'status')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude', 'zone')
        }),
        ('Auteur', {
            'fields': ('author',)
        }),
        ('Statistiques', {
            'fields': ('vote_count', 'positive_votes', 'negative_votes'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Administration des votes"""
    list_display = ['idea', 'user', 'is_positive', 'created_at']
    list_filter = ['is_positive', 'created_at']
    search_fields = ['idea__title', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
