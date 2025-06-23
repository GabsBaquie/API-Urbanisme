from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
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
    
    # Routes d'authentification JWT
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    
    # Routes JWT standard (optionnelles)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 