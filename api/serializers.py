from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # author = serializers.CharField(source='author.id')

    class Meta:
        model = Post
        fields = ['content', 'author', 'date_posted', 'number_of_likes']

    # def create(self, validated_data):
    #     return Post(**validated_data)
