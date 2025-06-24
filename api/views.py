from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Zone, Idea, Vote, Comment, CommentVote
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ZoneSerializer,
    IdeaSerializer, IdeaCreateSerializer, IdeaListSerializer, VoteSerializer,
    CommentSerializer, CommentCreateSerializer, CommentVoteSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour les utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Récupère les informations de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserRegistrationView(APIView):
    """Vue pour l'inscription des utilisateurs"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Utilisateur créé avec succès',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """Vue pour la connexion des utilisateurs avec JWT"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Connexion réussie',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        else:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """Vue pour la déconnexion des utilisateurs avec JWT"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Avec JWT, la déconnexion se fait côté client en supprimant le token
        # Optionnellement, on peut blacklister le token
        return Response({'message': 'Déconnexion réussie'})


class ZoneViewSet(viewsets.ModelViewSet):
    """ViewSet pour les zones géographiques"""
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    """Récupère tous les types d'une zone"""
    def get_queryset(self):
        queryset = Zone.objects.all()
        zone_type = self.request.query_params.get('zone_type')
        name = self.request.query_params.get('name')
        if zone_type:
            queryset = queryset.filter(zone_type=zone_type)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    
    @action(detail=True, methods=['get'])
    def ideas(self, request, pk=None):
        """Récupère toutes les idées d'une zone"""
        zone = self.get_object()
        ideas = zone.ideas.all()
        serializer = IdeaListSerializer(ideas, many=True)
        return Response(serializer.data)


class IdeaViewSet(viewsets.ModelViewSet):
    """ViewSet pour les idées"""
    queryset = Idea.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return IdeaCreateSerializer
        elif self.action == 'list':
            return IdeaListSerializer
        return IdeaSerializer

    def get_queryset(self):
        queryset = Idea.objects.all()
        
        # Filtres
        category = self.request.query_params.get('category', None)
        status = self.request.query_params.get('status', None)
        zone = self.request.query_params.get('zone', None)
        author = self.request.query_params.get('author', None)
        search = self.request.query_params.get('search', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        if zone:
            queryset = queryset.filter(zone_id=zone)
        if author:
            queryset = queryset.filter(author_id=author)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote sur une idée"""
        idea = self.get_object()
        is_positive = request.data.get('is_positive', True)
        
        # Vérifier si l'utilisateur a déjà voté
        existing_vote = Vote.objects.filter(idea=idea, user=request.user).first()
        
        if existing_vote:
            # Modifier le vote existant
            existing_vote.is_positive = is_positive
            existing_vote.save()
            message = "Vote modifié"
        else:
            # Créer un nouveau vote
            Vote.objects.create(
                idea=idea,
                user=request.user,
                is_positive=is_positive
            )
            message = "Vote ajouté"
        
        # Mettre à jour les statistiques de l'idée
        idea.update_vote_stats()
        
        return Response({
            'message': message,
            'idea': IdeaSerializer(idea, context={'request': request}).data
        })

    @action(detail=True, methods=['delete'])
    def unvote(self, request, pk=None):
        """Supprime le vote de l'utilisateur sur une idée"""
        idea = self.get_object()
        
        try:
            vote = Vote.objects.get(idea=idea, user=request.user)
            vote.delete()
            idea.update_vote_stats()
            
            return Response({
                'message': 'Vote supprimé',
                'idea': IdeaSerializer(idea, context={'request': request}).data
            })
        except Vote.DoesNotExist:
            return Response({
                'error': 'Aucun vote trouvé'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def near_me(self, request):
        """Récupère les idées proches de la position de l'utilisateur"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 1.0))  # Rayon en km
        
        if not lat or not lng:
            return Response({
                'error': 'Latitude et longitude requises'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcul simple de distance (approximation)
        lat, lng = float(lat), float(lng)
        lat_min, lat_max = lat - radius/111, lat + radius/111
        lng_min, lng_max = lng - radius/(111 * abs(lat)), lng + radius/(111 * abs(lat))
        
        ideas = Idea.objects.filter(
            latitude__range=(lat_min, lat_max),
            longitude__range=(lng_min, lng_max)
        )
        
        serializer = IdeaListSerializer(ideas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Gère les commentaires d'une idée"""
        idea = self.get_object()
        
        if request.method == 'GET':
            # Récupérer tous les commentaires de l'idée
            comments = idea.comments.all().order_by('-created_at')
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Créer un nouveau commentaire
            serializer = CommentCreateSerializer(
                data=request.data, 
                context={'request': request, 'idea': idea}
            )
            if serializer.is_valid():
                comment = serializer.save()
                return Response(
                    CommentSerializer(comment, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les votes"""
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    """Filtre par votes de l'utilisateur connecté et filtre par idées"""
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Vote.objects.filter(user=self.request.user)
        idea_id = self.request.query_params.get('idea_id', None)
        if idea_id:
            queryset = queryset.filter(idea_id=idea_id)
        return queryset
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commentaires"""
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        return Comment.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Seul l'auteur peut modifier son commentaire
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres commentaires.")
        serializer.save()

    def perform_destroy(self, instance):
        # Seul l'auteur peut supprimer son commentaire
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres commentaires.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote sur un commentaire"""
        comment = self.get_object()
        is_positive = request.data.get('is_positive', True)
        
        # Vérifier si l'utilisateur a déjà voté
        existing_vote = CommentVote.objects.filter(comment=comment, user=request.user).first()
        
        if existing_vote:
            # Modifier le vote existant
            existing_vote.is_positive = is_positive
            existing_vote.save()
            message = "Vote modifié"
        else:
            # Créer un nouveau vote
            CommentVote.objects.create(
                comment=comment,
                user=request.user,
                is_positive=is_positive
            )
            message = "Vote ajouté"
        
        return Response({
            'message': message,
            'comment': CommentSerializer(comment, context={'request': request}).data
        })

    @action(detail=True, methods=['delete'])
    def unvote(self, request, pk=None):
        """Supprime le vote de l'utilisateur sur un commentaire"""
        comment = self.get_object()
        
        try:
            vote = CommentVote.objects.get(comment=comment, user=request.user)
            vote.delete()
            
            return Response({
                'message': 'Vote supprimé',
                'comment': CommentSerializer(comment, context={'request': request}).data
            })
        except CommentVote.DoesNotExist:
            return Response({
                'error': 'Aucun vote trouvé'
            }, status=status.HTTP_404_NOT_FOUND)


class CommentVoteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les votes de commentaires"""
    queryset = CommentVote.objects.all()
    serializer_class = CommentVoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CommentVote.objects.filter(user=self.request.user)
        return CommentVote.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Seul l'utilisateur peut modifier son vote
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres votes.")
        serializer.save()

    def perform_destroy(self, instance):
        # Seul l'utilisateur peut supprimer son vote
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres votes.")
        instance.delete()
