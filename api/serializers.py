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

#TODO: METTRE A JOUR LE SERIALIZER POUR LES COMMENTAIRES AVEC LES NOMS ETC voir avec gabi
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
    user = serializers.SerializerMethodField()

    def get_user(self, obj: Vote):
        """Récupère l'utilisateur du vote"""
        return {
            'username': obj.user.username,
            'name': obj.user.get_full_name(),
        }


    class Meta:
        model = Vote
        fields = ['id', 'idea', 'user', 'is_positive', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CommentVoteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les votes de commentaires"""
    user = serializers.SerializerMethodField()

    def get_user(self, obj: CommentVote):
        """Récupère l'utilisateur du vote de commentaire"""
        return {
            'username': obj.user.username,
            'name': obj.user.get_full_name(),
        }
    class Meta:
        model = CommentVote
        fields = ['id', 'comment', 'user', 'is_positive']
        read_only_fields = ['id', 'user']


class CommentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les commentaires"""
    user = serializers.SerializerMethodField()
    votes = CommentVoteSerializer(many=True, read_only=True)

    def get_user(self, obj: Comment):
        """Récupère les informations de l'utilisateur du commentaire"""
        return {
            'username': obj.user.username,
            'name': obj.user.get_full_name(),
        }

    class Meta:
        model = Comment
        fields = ['id', 'idea', 'user', 'content', 
                 'created_at', 'updated_at', 'votes']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'votes']

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
    votes = VoteSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    position = serializers.SerializerMethodField()
    votesStats = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    zone = ZoneSerializer(read_only=True)

    def get_author(self, obj: Idea):
        """Récupère les informations de l'auteur de l'idée"""
        return {
            'username': obj.author.username,
            'name': obj.author.get_full_name()
        }

    def get_position(self, obj : Idea):
        return {
            'lat': obj.latitude,
            'lng': obj.longitude
        }
    
    def get_votesStats(self, obj: Idea):
        """Récupère les statistiques de vote pour l'idée"""
        return {
            'total': obj.vote_count,
            'up': obj.positive_votes,
            'down': obj.negative_votes
        }

    class Meta:
        model = Idea
        fields = ['id', 'title', 'description', 'category', 'status', 
                'position', 'author', 'zone', 'created_at', 'votesStats', 
                'votes', 'comments']
        read_only_fields = ['id', 'author', 'created_at', 'votes', 'comments']


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
    position = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    votesStats = serializers.SerializerMethodField()
    zone = ZoneSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)




    def get_author(self, obj: Idea):
        """Récupère les informations de l'auteur de l'idée"""
        return {
            'username': obj.author.username,
            'name': obj.author.get_full_name()
        }
    
    def get_position(self, obj: Idea):
        return {
            'lat': obj.latitude,
            'lng': obj.longitude
        }
    
    def get_votesStats(self, obj: Idea):
        """Récupère les statistiques de vote pour l'idée"""
        return {
            'total': obj.vote_count,
            'up': obj.positive_votes,
            'down': obj.negative_votes
        }


    class Meta:
        model = Idea
        fields = ['id', 'title', 'description', 'category', 'status', 'author', 'position',
                 'zone','votesStats', 'comments', 'created_at',] 