from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegistrationView, UserLoginView, UserLogoutView,
    ZoneViewSet, IdeaViewSet, VoteViewSet, CommentViewSet, CommentVoteViewSet
)

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'zones', ZoneViewSet)
router.register(r'ideas', IdeaViewSet)
router.register(r'votes', VoteViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'comment-votes', CommentVoteViewSet)

urlpatterns = [
    # Routes du router
    path('', include(router.urls)),
    
    # Routes d'authentification
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
] 