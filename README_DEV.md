# 🚀 Ma Rue Idéale - Guide Développeur

> API Django REST Framework pour la gestion d'idées citoyennes d'amélioration urbaine

## 📋 Table des matières

- [Installation](#-installation)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Modèles de données](#-modèles-de-données)
- [Authentification](#-authentification)
- [Développement](#-développement)
- [Tests](#-tests)
- [Déploiement](#-déploiement)

## ⚡ Installation

### Prérequis
- Python 3.8+
- pip
- Git

### Setup rapide
```bash
# 1. Cloner le projet
git clone <repository-url>
cd "Ma rue idéale"

# 2. Environnement virtuel
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. Base de données
python manage.py migrate

# 5. Données de test
python manage.py load_sample_data

# 6. Serveur de développement
python manage.py runserver
```

### Accès
- **API** : http://localhost:8000/api/
- **Admin** : http://localhost:8000/admin/
- **Comptes test** :
  - Admin : `admin@example.com` / `admin123`
  - Citoyen 1 : `citoyen1@example.com` / `password123`
  - Citoyen 2 : `citoyen2@example.com` / `password123`

## 🏗️ Architecture

### Stack technique
- **Backend** : Django 5.2.3
- **API** : Django REST Framework 3.16.0
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Authentification** : Session Django
- **CORS** : django-cors-headers

### Structure du projet
```
ma_rue_ideale/
├── api/                    # Application principale
│   ├── models.py          # Modèles de données
│   ├── serializers.py     # Sérialiseurs API
│   ├── views.py           # Vues et ViewSets
│   ├── urls.py            # Routes API
│   ├── admin.py           # Interface d'administration
│   └── management/        # Commandes personnalisées
├── ma_rue_ideale/         # Configuration Django
│   ├── settings.py        # Paramètres
│   └── urls.py            # Routes principales
├── requirements.txt       # Dépendances
└── README.md             # Documentation utilisateur
```

## 📚 API Reference

### Base URL
```
http://localhost:8000/api/
```

### Authentification

#### Inscription
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "dev_user",
    "email": "dev@example.com",
    "password": "password123",
    "password_confirm": "password123"
}
```

#### Connexion
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "dev@example.com",
    "password": "password123"
}
```

#### Déconnexion
```http
POST /api/auth/logout/
```

### Utilisateurs

#### Profil utilisateur
```http
GET /api/users/me/
Authorization: Session
```

### Idées

#### Liste des idées
```http
GET /api/ideas/
```

**Paramètres de filtrage :**
- `category` : mobilité, végétation, mobilier urbain, etc.
- `status` : proposée, en cours d'examen, approuvée, etc.
- `zone` : ID de la zone
- `author` : ID de l'auteur
- `search` : recherche dans le titre et la description

**Exemples :**
```bash
# Idées de mobilité
GET /api/ideas/?category=mobility

# Idées en cours d'examen
GET /api/ideas/?status=under_review

# Recherche
GET /api/ideas/?search=bancs

# Idées d'une zone
GET /api/ideas/?zone=1
```

#### Détail d'une idée
```http
GET /api/ideas/{id}/
```

#### Créer une idée
```http
POST /api/ideas/
Content-Type: application/json
Authorization: Session

{
    "title": "Nouvelle idée",
    "description": "Description détaillée...",
    "category": "furniture",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "zone": 1
}
```

#### Idées proches
```http
GET /api/ideas/near_me/?lat=48.8566&lng=2.3522&radius=1.0
```

### Votes

#### Voter sur une idée
```http
POST /api/ideas/{id}/vote/
Content-Type: application/json
Authorization: Session

{
    "is_positive": true
}
```

#### Supprimer un vote
```http
DELETE /api/ideas/{id}/unvote/
Authorization: Session
Authorization: Bearer <access_token>
```

### Commentaires

#### Liste des commentaires d'une idée
```http
GET /api/ideas/{id}/comments/
```

#### Détail d'un commentaire
```http
GET /api/comments/{id}/
```

#### Créer un commentaire
```http
POST /api/ideas/{id}/comments/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie dans le quartier."
}
```

#### Modifier un commentaire
```http
PUT /api/comments/{id}/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "content": "Commentaire modifié"
}
```

#### Supprimer un commentaire
```http
DELETE /api/comments/{id}/
Authorization: Bearer <access_token>
```

### Votes de commentaires

#### Voter sur un commentaire
```http
POST /api/comments/{id}/vote/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "is_positive": true
}
```

#### Supprimer un vote sur un commentaire
```http
DELETE /api/comments/{id}/unvote/
Authorization: Bearer <access_token>
```

### Zones

#### Liste des zones
```http
GET /api/zones/
```

#### Détail d'une zone
```http
GET /api/zones/{id}/
```

#### Idées d'une zone
```http
GET /api/zones/{id}/ideas/
```

## 🗄️ Modèles de données

### User
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Zone
```python
class Zone(models.Model):
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
```

### Idea
```python
class Idea(models.Model):
    CATEGORIES = [
        ('mobility', 'Mobilité'),
        ('greenery', 'Végétation'),
        ('furniture', 'Mobilier urbain'),
        ('safety', 'Sécurité'),
        ('culture', 'Culture'),
        ('sport', 'Sport'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposée'),
        ('under_review', 'En cours d\'examen'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
        ('implemented', 'Implémentée'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='ideas')
    vote_count = models.IntegerField(default=0)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
```

### Vote
```python
class Vote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    is_positive = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['idea', 'user']
```

### Comment
```python
class Comment(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### CommentVote
```python
class CommentVote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    is_positive = models.BooleanField()
    
    class Meta:
        unique_together = ['comment', 'user']
```

## 🔐 Authentification

### Méthode
- **Session Django** : Authentification par session
- **CSRF** : Protection CSRF activée
- **Permissions** : Basées sur les rôles Django

### Permissions par défaut
- **Lecture** : Publique (`IsAuthenticatedOrReadOnly`)
- **Écriture** : Authentifiée (`IsAuthenticated`)
- **Admin** : Staff Django

### Headers requis
```javascript
const headers = {
  'Content-Type': 'application/json',
  'X-CSRFToken': getCookie('csrftoken'), // Pour les requêtes POST/PUT/DELETE
};
```

## 🛠️ Développement

### Commandes utiles
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Voir les migrations
python manage.py showmigrations

# Créer une migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Charger les données de test
python manage.py load_sample_data

# Collecter les fichiers statiques
python manage.py collectstatic
```

### Variables d'environnement
```bash
# .env (à créer)
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Configuration de développement
```python
# settings.py
DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Logs
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 🧪 Tests

### Structure des tests
```
api/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_api.py
```

### Exécuter les tests
```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test api.tests.test_api

# Avec couverture
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Tests API avec curl
```bash
# Test d'inscription
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","password_confirm":"test123"}'

# Test de connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test récupération idées
curl http://localhost:8000/api/ideas/

# Test récupération profil (authentifié)
curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8000/api/users/me/

# Test création d'idée (authentifié)
curl -X POST http://localhost:8000/api/ideas/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title":"Test","description":"Test","category":"other","latitude":48.8566,"longitude":2.3522,"zone":1}'

# Test création de commentaire (authentifié)
curl -X POST http://localhost:8000/api/ideas/1/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"content":"Excellente idée !"}'

# Test vote sur commentaire (authentifié)
curl -X POST http://localhost:8000/api/comments/1/vote/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"is_positive":true}'

# Test rafraîchissement de token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

## 🚀 Déploiement

### Production
```bash
# 1. Variables d'environnement
export SECRET_KEY="your-production-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com"

# 2. Base de données PostgreSQL
pip install psycopg2-binary

# 3. Serveur WSGI
pip install gunicorn

# 4. Collecter les statiques
python manage.py collectstatic

# 5. Migrations
python manage.py migrate

# 6. Lancer avec Gunicorn
gunicorn ma_rue_ideale.wsgi:application
```

### Docker (optionnel)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "ma_rue_ideale.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Health check
```http
GET /api/health/
```

### Métriques
- Nombre d'idées par catégorie
- Taux d'approbation des idées
- Activité utilisateur
- Performance des endpoints

## 🔧 Debugging

### Debug Django
```python
import pdb; pdb.set_trace()
```

### Debug API
```python
from rest_framework.test import APITestCase
from rest_framework import status

class IdeaAPITestCase(APITestCase):
    def test_create_idea(self):
        # Test code here
        pass
```

### Logs de développement
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## 📝 Bonnes pratiques

### Code
- Suivre PEP 8
- Docstrings pour toutes les fonctions
- Tests unitaires
- Validation des données

### API
- Versioning des endpoints
- Pagination systématique
- Gestion d'erreurs cohérente
- Documentation OpenAPI/Swagger

### Sécurité
- Validation côté serveur
- Protection CSRF
- Rate limiting
- Audit des actions sensibles

## 🆘 Support

### Ressources
- [Documentation Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Admin](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)

### Contacts
- Issues : GitHub Issues
- Documentation : README.md
- Admin : Interface Django Admin

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2025-06-23  
**Mainteneur** : Équipe de développement