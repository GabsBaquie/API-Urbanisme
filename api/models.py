from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Modèle utilisateur étendu"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_anonymous = models.BooleanField(default=False) # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class Zone(models.Model):
    """Zone géographique (quartier, rue, etc.)"""
    ZONE_TYPES = [
        ('neighborhood', 'Quartier'),
        ('street', 'Rue'),
        ('district', 'Arrondissement'),
        ('city', 'Ville'),
    ]

    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        # Use get_zone_type_display if available, else fallback to zone_type
        display = getattr(self, "get_zone_type_display", None)
        if callable(display):
            zone_type_display = self.get_zone_type_display() # type: ignore
        else:
            zone_type_display = self.zone_type
        return f"{self.name} ({zone_type_display})"

class Idea(models.Model):
    """Idée d'amélioration proposée par un citoyen"""
    class CATEGORIES(models.TextChoices):
        AMENAGEMENT = 'AMENAGEMENT', 'Aménagement'
        ENVIRONNEMENT = 'ENVIRONNEMENT', 'Environnement'
        TRANSPORT = 'TRANSPORT', 'Transport'
        SOCIAL = 'SOCIAL', 'Social'

    class STATUS(models.TextChoices):
        PROPOSED = 'PROPOSED', 'Proposée'
        UNDER_REVIEW = 'UNDER_REVIEW', 'En cours d\'examen'
        APPROVED = 'APPROVED', 'Approuvée'
        REJECTED = 'REJECTED', 'Rejetée'
        IMPLEMENTED = 'IMPLEMENTED', 'Implémentée'

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(choices=CATEGORIES)
    status = models.CharField(choices=STATUS, default=STATUS.PROPOSED)
    
    # Géolocalisation
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='ideas')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistiques
    vote_count = models.IntegerField(default=0)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def update_vote_stats(self):
        """Met à jour les statistiques de vote"""
        votes = self.votes.all() # type: ignore
        self.vote_count = votes.count()
        self.positive_votes = votes.filter(is_positive=True).count()
        self.negative_votes = votes.filter(is_positive=False).count()
        self.save()

class Vote(models.Model):
    """Vote sur une idée"""
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    is_positive = models.BooleanField()  # True = vote positif, False = vote négatif
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['idea', 'user']
        ordering = ['-created_at']

    def __str__(self):
        vote_type = "positif" if self.is_positive else "négatif"
        return f"Vote {vote_type} de {self.user.email} sur {self.idea.title}"

    def save(self, *args, **kwargs):
        """Sauvegarde le vote et met à jour les statistiques de l'idée"""
        super().save(*args, **kwargs)
        self.idea.update_vote_stats()

class Comment(models.Model):
    """Commentaire sur une idée"""
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.idea.title}"

class CommentVote(models.Model):
    """Vote sur un commentaire"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    is_positive = models.BooleanField()  # True = vote positif, False = vote négatif

    class Meta:
        unique_together = ['comment', 'user']

    def __str__(self):
        vote_type = "positif" if self.is_positive else "négatif"
        return f"Vote {vote_type} de {self.user.username} sur {self.comment.idea.title}"
