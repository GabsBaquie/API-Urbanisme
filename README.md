# Ma Rue Idéale - API Backend

Une API Django REST Framework pour permettre aux citoyens de proposer des idées d'amélioration pour leur quartier sur une carte interactive.

## 🎯 Fonctionnalités

- **Gestion des utilisateurs** : Inscription, connexion, profil
- **Zones géographiques** : Quartiers, rues, arrondissements
- **Idées citoyennes** : Propositions d'amélioration avec géolocalisation
- **Système de votes** : Vote positif/négatif sur les idées
- **Interface d'administration** : Gestion complète via Django Admin

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd "Ma rue idéale"
```

2. **Créer l'environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install django djangorestframework django-cors-headers
```

4. **Configurer la base de données**
```bash
python manage.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Charger les données d'exemple (optionnel)**
```bash
python manage.py load_sample_data
```

7. **Lancer le serveur**
```bash
python manage.py runserver
```

## 📚 API Endpoints

### Authentification

#### Inscription
```
POST /api/auth/register/
```
```json
{
    "username": "citoyen",
    "email": "citoyen@example.com",
    "password": "motdepasse123",
    "password_confirm": "motdepasse123"
}
```

#### Connexion
```
POST /api/auth/login/
```
```json
{
    "email": "citoyen@example.com",
    "password": "motdepasse123"
}
```

#### Déconnexion
```
POST /api/auth/logout/
```

### Utilisateurs

#### Profil utilisateur
```
GET /api/users/me/
```

### Zones géographiques

#### Liste des zones
```
GET /api/zones/
```

#### Détail d'une zone
```
GET /api/zones/{id}/
```

#### Idées d'une zone
```
GET /api/zones/{id}/ideas/
```

### Idées

#### Liste des idées
```
GET /api/ideas/
```

Paramètres de filtrage :
- `category` : mobilité, végétation, mobilier urbain, etc.
- `status` : proposée, en cours d'examen, approuvée, etc.
- `zone` : ID de la zone
- `author` : ID de l'auteur
- `search` : recherche dans le titre et la description

#### Détail d'une idée
```
GET /api/ideas/{id}/
```

#### Créer une idée
```
POST /api/ideas/
```
```json
{
    "title": "Ajouter des bancs",
    "description": "Il manque de bancs pour se reposer",
    "category": "furniture",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "zone": 1
}
```

#### Idées proches
```
GET /api/ideas/near_me/?lat=48.8566&lng=2.3522&radius=1.0
```

### Votes

#### Voter sur une idée
```
POST /api/ideas/{id}/vote/
```
```json
{
    "is_positive": true
}
```

#### Supprimer un vote
```
DELETE /api/ideas/{id}/unvote/
```

### Commentaires

#### Liste des commentaires d'une idée
```
GET /api/ideas/{id}/comments/
```

#### Détail d'un commentaire
```
GET /api/comments/{id}/
```

#### Créer un commentaire
```
POST /api/ideas/{id}/comments/
```
```json
{
    "content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie dans le quartier."
}
```

#### Modifier un commentaire
```
PUT /api/comments/{id}/
```
```json
{
    "content": "Commentaire modifié"
}
```

#### Supprimer un commentaire
```
DELETE /api/comments/{id}/
```

### Votes de commentaires

#### Voter sur un commentaire
```
POST /api/comments/{id}/vote/
```
```json
{
    "is_positive": true
}
```

#### Supprimer un vote sur un commentaire
```
DELETE /api/comments/{id}/unvote/
```

## 🗄️ Modèles de données

### User
- `email` : Email unique (identifiant de connexion)
- `username` : Nom d'utilisateur
- `is_anonymous` : Utilisateur anonyme ou non
- `created_at` : Date de création

### Zone
- `name` : Nom de la zone
- `zone_type` : Type (quartier, rue, arrondissement, ville)
- `latitude` / `longitude` : Coordonnées géographiques
- `description` : Description de la zone

### Idea
- `title` : Titre de l'idée
- `description` : Description détaillée
- `category` : Catégorie (mobilité, végétation, etc.)
- `status` : Statut (proposée, approuvée, etc.)
- `latitude` / `longitude` : Position précise
- `author` : Auteur de l'idée
- `zone` : Zone géographique
- `vote_count` : Nombre total de votes
- `positive_votes` : Votes positifs
- `negative_votes` : Votes négatifs

### Vote
- `idea` : Idée votée
- `user` : Utilisateur qui vote
- `is_positive` : Vote positif ou négatif
- `created_at` : Date du vote

### Comment
- `idea` : Idée commentée
- `user` : Auteur du commentaire
- `content` : Contenu du commentaire
- `created_at` : Date de création
- `updated_at` : Date de modification

### CommentVote
- `comment` : Commentaire voté
- `user` : Utilisateur qui vote
- `is_positive` : Vote positif ou négatif

## 🔧 Configuration

### Variables d'environnement
- `SECRET_KEY` : Clé secrète Django
- `DEBUG` : Mode debug (True/False)
- `ALLOWED_HOSTS` : Hôtes autorisés

### Base de données
Par défaut, l'application utilise SQLite. Pour PostgreSQL :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ma_rue_ideale',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🛠️ Administration

Accédez à l'interface d'administration à l'adresse `/admin/` avec les identifiants du superutilisateur.

### Comptes de test
- **Admin** : `admin@example.com` / `admin123`
- **Citoyen 1** : `citoyen1@example.com` / `password123`
- **Citoyen 2** : `citoyen2@example.com` / `password123`

## 📊 Exemples d'utilisation

### Récupérer toutes les idées de mobilité
```bash
curl "http://localhost:8000/api/ideas/?category=mobility"
```

### Créer une nouvelle idée
```bash
curl -X POST "http://localhost:8000/api/ideas/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Piste cyclable",
    "description": "Créer une piste cyclable sécurisée",
    "category": "mobility",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "zone": 1
  }'
```

### Voter sur une idée
```bash
curl -X POST "http://localhost:8000/api/ideas/1/vote/" \
  -H "Content-Type: application/json" \
  -d '{"is_positive": true}'
```

### Créer un commentaire sur une idée
```bash
curl -X POST "http://localhost:8000/api/ideas/1/comments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie."}'
```

### Voter sur un commentaire
```bash
curl -X POST "http://localhost:8000/api/comments/1/vote/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"is_positive": true}'
```

### Créer un commentaire sur une idée
```bash
curl -X POST "http://localhost:8000/api/ideas/1/comments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie."}'
```

### Voter sur un commentaire
```bash
curl -X POST "http://localhost:8000/api/comments/1/vote/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"is_positive": true}'
```

### Créer un commentaire sur une idée
```bash
curl -X POST "http://localhost:8000/api/ideas/1/comments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie."}'
```

### Voter sur un commentaire
```bash
curl -X POST "http://localhost:8000/api/comments/1/vote/" \
  -H "Content-Type: application/json" \
  -d '{"is_positive": true}'
```

### Créer un commentaire sur une idée
```bash
curl -X POST "http://localhost:8000/api/ideas/1/comments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"content": "Excellente idée ! Cela améliorerait vraiment la qualité de vie."}'
```

### Voter sur un commentaire
```bash
curl -X POST "http://localhost:8000/api/comments/1/vote/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
  -d '{"is_positive": true}'
```

### Rafraîchir un token expiré
```bash
curl -X POST "http://localhost:8000/api/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<votre_refresh_token>"}'
```

## 🔒 Sécurité

- Authentification par session Django
- Permissions basées sur les rôles
- Validation des données côté serveur
- Protection CSRF activée

## 🚀 Déploiement

### Production
1. Configurer `DEBUG = False`
2. Utiliser une base de données PostgreSQL
3. Configurer les variables d'environnement
4. Utiliser un serveur WSGI (Gunicorn)
5. Configurer un reverse proxy (Nginx)

### Variables d'environnement recommandées
```bash
export SECRET_KEY="votre-clé-secrète"
export DEBUG=False
export ALLOWED_HOSTS="votre-domaine.com"
```

## 📝 Licence

Ce projet est sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request 