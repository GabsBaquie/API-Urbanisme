# Ma Rue Idéale - API Backend

Une API Django REST Framework pour permettre aux citoyens de proposer des idées d'amélioration pour leur quartier sur une carte interactive.

## 🎯 Fonctionnalités

- **Gestion des utilisateurs** : Inscription, connexion, profil
- **Zones géographiques** : Quartiers, rues, arrondissements
- **Idées citoyennes** : Propositions d'amélioration avec géolocalisation
- **Système de votes** : Vote positif/négatif sur les idées
- **Interface d'administration** : Gestion complète via Django Admin
- **Authentification JWT** : Tokens sécurisés pour l'API

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
pip install -r requirements.txt
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

### Authentification JWT

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

**Réponse :**
```json
{
    "message": "Connexion réussie",
    "user": {
        "id": 1,
        "username": "citoyen",
        "email": "citoyen@example.com",
        "is_anonymous": false,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Rafraîchir le token
```
POST /api/auth/token/refresh/
```
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Déconnexion
```
POST /api/auth/logout/
```
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Utilisation des tokens JWT

Pour les requêtes authentifiées, incluez le token d'accès dans l'en-tête Authorization :

```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
     http://localhost:8000/api/users/me/
```

### Workflow d'authentification JWT

1. **Inscription** : L'utilisateur s'inscrit via `/api/auth/register/`
2. **Connexion** : L'utilisateur se connecte via `/api/auth/login/` et reçoit :
   - Un token d'accès (valide 1 heure)
   - Un token de rafraîchissement (valide 1 jour)
3. **Utilisation** : Inclure le token d'accès dans l'en-tête `Authorization: Bearer <token>`
4. **Rafraîchissement** : Quand le token d'accès expire, utiliser le refresh token via `/api/auth/token/refresh/`
5. **Déconnexion** : Invalider le refresh token via `/api/auth/logout/`

### Gestion des tokens côté client

```javascript
// Exemple JavaScript pour gérer les tokens
class AuthService {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    async login(email, password) {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (response.ok) {
            this.accessToken = data.tokens.access;
            this.refreshToken = data.tokens.refresh;
            localStorage.setItem('access_token', this.accessToken);
            localStorage.setItem('refresh_token', this.refreshToken);
            return data;
        }
        throw new Error(data.error);
    }

    async refreshAccessToken() {
        const response = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: this.refreshToken })
        });
        
        const data = await response.json();
        if (response.ok) {
            this.accessToken = data.access;
            localStorage.setItem('access_token', this.accessToken);
            return data.access;
        }
        throw new Error('Token refresh failed');
    }

    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.accessToken) {
            throw new Error('No access token');
        }

        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${this.accessToken}`
            }
        });

        if (response.status === 401) {
            // Token expiré, essayer de le rafraîchir
            try {
                await this.refreshAccessToken();
                // Réessayer la requête avec le nouveau token
                return fetch(url, {
                    ...options,
                    headers: {
                        ...options.headers,
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                });
            } catch (error) {
                // Refresh échoué, rediriger vers la connexion
                this.logout();
                throw error;
            }
        }

        return response;
    }

    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
}
```

### Utilisateurs

#### Profil utilisateur
```
GET /api/users/me/
```
**Headers requis :** `Authorization: Bearer <access_token>`

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

### Connexion et récupération du token
```bash
# 1. Se connecter
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"citoyen1@example.com","password":"password123"}'

# 2. Utiliser le token pour récupérer le profil
curl -H "Authorization: Bearer <votre_access_token>" \
     "http://localhost:8000/api/users/me/"
```

### Récupérer toutes les idées de mobilité
```bash
curl "http://localhost:8000/api/ideas/?category=mobility"
```

### Créer une nouvelle idée
```bash
curl -X POST "http://localhost:8000/api/ideas/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <votre_access_token>" \
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

- **Authentification JWT** : Tokens d'accès et de rafraîchissement sécurisés
- **Durée de vie des tokens** : 
  - Access token : 1 heure
  - Refresh token : 1 jour
- **Algorithme** : HS256 avec clé secrète Django
- **Permissions** : Basées sur les rôles Django
- **Validation des données** : Côté serveur
- **CORS** : Configuré pour le développement

### Configuration JWT
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

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
export JWT_SECRET_KEY="votre-clé-jwt-secrète"  # Optionnel, utilise SECRET_KEY par défaut
```

### Configuration JWT en production
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Plus long en production
    'ROTATE_REFRESH_TOKENS': True,  # Sécurité renforcée
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
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