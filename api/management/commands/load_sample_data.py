from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Zone, Idea, Vote

User = get_user_model()


class Command(BaseCommand):
    help = 'Charge des données d\'exemple pour l\'application'

    def handle(self, *args, **options):
        self.stdout.write('Chargement des données d\'exemple...')

        # Créer des utilisateurs de test
        if not User.objects.filter(email='citoyen1@example.com').exists():
            user1 = User.objects.create_user(
                username='citoyen1',
                email='citoyen1@example.com',
                password='password123'
            )
            self.stdout.write(f'Utilisateur créé: {user1.email}')
        else:
            user1 = User.objects.get(email='citoyen1@example.com')

        if not User.objects.filter(email='citoyen2@example.com').exists():
            user2 = User.objects.create_user(
                username='citoyen2',
                email='citoyen2@example.com',
                password='password123'
            )
            self.stdout.write(f'Utilisateur créé: {user2.email}')
        else:
            user2 = User.objects.get(email='citoyen2@example.com')

        # Créer des zones géographiques
        zones_data = [
            {
                'name': 'Quartier de la Gare',
                'zone_type': 'neighborhood',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'description': 'Quartier animé autour de la gare principale'
            },
            {
                'name': 'Rue de la Paix',
                'zone_type': 'street',
                'latitude': 48.8584,
                'longitude': 2.2945,
                'description': 'Rue commerçante du centre-ville'
            },
            {
                'name': 'Parc Central',
                'zone_type': 'neighborhood',
                'latitude': 48.8606,
                'longitude': 2.3376,
                'description': 'Zone verte avec espaces de détente'
            }
        ]

        zones = []
        for zone_data in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            zones.append(zone)
            if created:
                self.stdout.write(f'Zone créée: {zone.name}')

        # Créer des idées
        ideas_data = [
            {
                'title': 'Ajouter des bancs dans le parc',
                'description': 'Il manque de bancs pour se reposer dans le parc central. Cela permettrait aux personnes âgées et aux familles de profiter davantage de cet espace.',
                'category': 'furniture',
                'latitude': 48.8606,
                'longitude': 2.3376,
                'zone': zones[2],
                'author': user1
            },
            {
                'title': 'Piste cyclable sécurisée',
                'description': 'Créer une piste cyclable séparée de la circulation automobile pour améliorer la sécurité des cyclistes.',
                'category': 'mobility',
                'latitude': 48.8584,
                'longitude': 2.2945,
                'zone': zones[1],
                'author': user2
            },
            {
                'title': 'Plus d\'arbres en ville',
                'description': 'Planter plus d\'arbres pour améliorer la qualité de l\'air et créer plus d\'ombre en été.',
                'category': 'greenery',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'zone': zones[0],
                'author': user1
            },
            {
                'title': 'Éclairage LED éco-responsable',
                'description': 'Remplacer l\'éclairage public par des LED pour réduire la consommation d\'énergie.',
                'category': 'safety',
                'latitude': 48.8584,
                'longitude': 2.2945,
                'zone': zones[1],
                'author': user2
            },
            {
                'title': 'Mur d\'escalade urbain',
                'description': 'Installer un mur d\'escalade dans le parc pour les jeunes et les sportifs.',
                'category': 'sport',
                'latitude': 48.8606,
                'longitude': 2.3376,
                'zone': zones[2],
                'author': user1
            }
        ]

        ideas = []
        for idea_data in ideas_data:
            idea, created = Idea.objects.get_or_create(
                title=idea_data['title'],
                defaults=idea_data
            )
            ideas.append(idea)
            if created:
                self.stdout.write(f'Idée créée: {idea.title}')

        # Créer des votes
        votes_data = [
            {'idea': ideas[0], 'user': user1, 'is_positive': True},
            {'idea': ideas[0], 'user': user2, 'is_positive': True},
            {'idea': ideas[1], 'user': user1, 'is_positive': True},
            {'idea': ideas[1], 'user': user2, 'is_positive': False},
            {'idea': ideas[2], 'user': user1, 'is_positive': True},
            {'idea': ideas[2], 'user': user2, 'is_positive': True},
            {'idea': ideas[3], 'user': user1, 'is_positive': False},
            {'idea': ideas[4], 'user': user2, 'is_positive': True},
        ]

        for vote_data in votes_data:
            vote, created = Vote.objects.get_or_create(
                idea=vote_data['idea'],
                user=vote_data['user'],
                defaults={'is_positive': vote_data['is_positive']}
            )
            if created:
                vote_type = "positif" if vote.is_positive else "négatif"
                self.stdout.write(f'Vote {vote_type} créé pour {vote.idea.title}')

        # Mettre à jour les statistiques des idées
        for idea in ideas:
            idea.update_vote_stats()

        self.stdout.write(
            self.style.SUCCESS('Données d\'exemple chargées avec succès!')
        ) 