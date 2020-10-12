from django.http import HttpResponse
from .serializers import PostSerializer, UserSerializer, LikeSerializer, LikeAggrSerializer, UserStatsSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Post, Like, Profile
from django.contrib.auth.models import User
from rest_framework.permissions import  AllowAny
import random
import datetime
from django.db.models import Count
from django.contrib.admin.models import LogEntry
from django.db.models import Max
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import CustomTokenObtainPairSerializer


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ListAllAPIView(APIView):
    def get(self, request):
        """Listing all posts"""
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class CreatePostAPIView(APIView):
    def post(self, request):
        """Creating new post"""
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = CustomTokenObtainPairSerializer


def get_object(id, model):
    try:
        return model.objects.get(id=id)
    except model.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def serialize(post):
    serializer = PostSerializer(post)
    serialized_data = serializer.data
    serializer = PostSerializer(post, data=serialized_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikePostAPIView(APIView):
    def post(self, request, post_id):
        if int(post_id) == 0:                   # selecting a random post to like if post_id = 0 was passed (for bot)
            posts = Post.objects.all()
            random_item = random.choice(posts)  # randomly chooses item
            post_id = random_item.id

        path = request.get_full_path()  # /api/like/<int:id>
        if '/like' in path:
            like_value = +1
        elif '/unlike' in path:
            like_value = -1

        # Making +1 or -1 in Post model's number_of likes
        post_obj = get_object(post_id, Post)
        post_obj.number_of_likes += like_value
        if post_obj.number_of_likes < 0:        # if we unlike the 0-liked posted, let's stay with 0, not -1
            post_obj.number_of_likes = 0
        post_obj.save()

        # Creating a like instance with timestamp + user and post references
        like = Like()
        user = User.objects.get(username=request.data['author'])   # get_object(request.data['author'], User)
        like.user = user
        like.post = post_obj
        like.value = like_value
        like.save()

        like_unlike = 'like' if like_value > 0 else 'unlike'
        print('Post with id = {} {}d by user: {}.'.format(post_id, like_unlike, user))
        return serialize(post_obj)


class UnlikePostAPIView(APIView):
    def unlike(self, request, postid):
        pass


class DeletePostAPIView(APIView):
    def delete(self, request, id):
        """Delete post by id"""
        post = get_object(id, Post)
        post.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


def get_dates_from_request(request):
    if 'date_from' in request.GET:
        date_from = request.GET['date_from']
    else:
        date_from = '2004-02-04'  # facebook launch date
        # (we cannot launch our social network before Facebook, can we?)
    if 'date_to' in request.GET:
        date_to = request.GET['date_to']
    else:
        date_to = datetime.datetime.today()

    error = ''
    try:  # checking if dates are correct and if date_from > date to
        if not isinstance(date_from, datetime.datetime):
            date1 = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        else:
            date1 = date_from

        if not isinstance(date_to, datetime.datetime):
            date2 = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        else:
            date2 = date_to
        if date1 > date2:
            error = Response('Incorrect dates provided: date_from > date_to')
    except ValueError:
        error = Response('Incorrect dates provided.')

    return date_from, date_to, error


class LikesFilteredByDateAPIView(APIView):
    model = Like

    def get(self, request):
        date_from, date_to, error = get_dates_from_request(request)
        if error != '':
            return error

        likes = Like.objects.filter(date__gte=date_from, date__lte=date_to)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)


class LikesAggregatedByDaysAPIView(APIView):
    model = Like

    def get(self, request):
        date_from, date_to, error = get_dates_from_request(request)
        if error != '':
            return error

        likes = Like.objects.extra(select={'day': 'date( date )'}).values('day') \
            .annotate(liked_posts=Count('date'))

        serializer = LikeAggrSerializer(likes, many=True)
        return Response(serializer.data)


class FilterPostsByDateAPIView(APIView):
    model = Post

    def get(self, request):
        date_from, date_to, error = get_dates_from_request(request)
        if error != '':
            return error

        posts = Post.objects.filter(date_posted__gte=date_from, date_posted__lte=date_to)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class UserStatsAPIView(APIView):
    # model = Profile
    model = User

    def get(self, request):
        users = User.objects.all()
        serializer = UserStatsSerializer(users, many=True)
        return Response(serializer.data)


class PostListView(ListView):
    model = Post
    template_name = 'api/home.html'
    context_object_name = 'posts'
    ordering = ['-id']


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
