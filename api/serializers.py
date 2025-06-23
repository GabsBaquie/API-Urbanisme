from rest_framework import serializers
from .models import User, Zone, Idea, Vote, Comment, CommentVote


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_anonymous', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ZoneSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les zones géographiques"""
    zone_type_display = serializers.CharField(source='get_zone_type_display', read_only=True)
    idea_count = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = ['id', 'name', 'zone_type', 'zone_type_display', 'latitude', 'longitude', 
                 'description', 'created_at', 'idea_count']
        read_only_fields = ['id', 'created_at']

    def get_idea_count(self, obj):
        return obj.ideas.count()


class VoteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les votes"""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'idea', 'user', 'user_email', 'is_positive', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CommentVoteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les votes de commentaires"""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = CommentVote
        fields = ['id', 'comment', 'user', 'user_email', 'is_positive']
        read_only_fields = ['id', 'user']


class CommentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les commentaires"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    votes = CommentVoteSerializer(many=True, read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'idea', 'user', 'user_email', 'user_username', 'content', 
                 'created_at', 'updated_at', 'votes', 'user_vote']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'votes', 'user_vote']

    def get_user_vote(self, obj):
        """Récupère le vote de l'utilisateur connecté sur ce commentaire"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.votes.get(user=request.user)
                return {
                    'id': vote.id,
                    'is_positive': vote.is_positive
                }
            except CommentVote.DoesNotExist:
                return None
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de commentaires"""
    class Meta:
        model = Comment
        fields = ['content']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['idea'] = self.context['idea']
        return super().create(validated_data)


class IdeaSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les idées"""
    author_email = serializers.CharField(source='author.email', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    votes = VoteSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ['id', 'title', 'description', 'category', 'category_display', 'status', 
                 'status_display', 'latitude', 'longitude', 'author', 'author_email', 
                 'zone', 'zone_name', 'created_at', 'vote_count', 'positive_votes', 
                 'negative_votes', 'votes', 'comments', 'user_vote']
        read_only_fields = ['id', 'author', 'created_at', 'vote_count', 'positive_votes', 
                           'negative_votes', 'votes', 'comments', 'user_vote']

    def get_user_vote(self, obj):
        """Récupère le vote de l'utilisateur connecté sur cette idée"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.votes.get(user=request.user)
                return {
                    'id': vote.id,
                    'is_positive': vote.is_positive,
                    'created_at': vote.created_at
                }
            except Vote.DoesNotExist:
                return None
        return None


class IdeaCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'idées"""
    class Meta:
        model = Idea
        fields = ['title', 'description', 'category', 'latitude', 'longitude', 'zone']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class IdeaListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des idées"""
    author_email = serializers.CharField(source='author.email', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Idea
        fields = ['id', 'title', 'category', 'category_display', 'status', 'status_display',
                 'latitude', 'longitude', 'author_email', 'zone_name', 'created_at',
                 'vote_count', 'positive_votes', 'negative_votes'] 