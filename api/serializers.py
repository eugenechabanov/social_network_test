from rest_framework import serializers
from .models import Post, Like, Profile
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'image', 'date_posted', 'number_of_likes']
        # fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class LikeAggrSerializer(serializers.Serializer):
    day = serializers.DateTimeField()
    liked_posts = serializers.IntegerField()


class UserStatsSerializer(serializers.ModelSerializer):
    last_action = serializers.DateTimeField(source='profile.last_action')

    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'last_action')


class LogEntrySerializer(serializers.Serializer):
    class Meta:
        model = LogEntry
        fields = ('user_id', 'action_time')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        print(self.user.id)
        p = Profile.objects.get(user_id=self.user.id)
        p.last_action = timezone.now()
        p.save()
        return data
