from django.http import HttpResponse
from .serializers import PostSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from .models import Post
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny


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
        # print(request.data)
        # print(User.objects.all())
        # # request.data['author'] = 3  # author name
        # data = request.data
        # s = User.objects.get(username=request.data['author'])
        # data['author_id'] = s.id
        # print(data)
        # author = self.get_queryset().latest('publication_date')

        serializer = PostSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_object(id):
    try:
        return Post.objects.get(id=id)
    except Post.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def like_or_dislike(id, i):
    """Edit post by id"""
    post = get_object(id)
    post.number_of_likes += i       # i is either +1 or -1
    if post.number_of_likes < 0:    # just in case so we don't slide off the set of natural numbers
        post.number_of_likes = 0
    post.save()
    serializer = PostSerializer(post)
    serialized_data = serializer.data
    serializer = PostSerializer(post, data=serialized_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikePostAPIView(APIView):
    def put(self, request, id):
        return like_or_dislike(id, 1)


class UnlikePostAPIView(APIView):
    def put(self, request, id):
        return  like_or_dislike(id, -1)


class DeletePostAPIView(APIView):
    def delete(self, request, id):
        """Delete post by id"""
        post = get_object(id)
        post.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'api/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'api/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']


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


# def about(request):
#     return render(request, 'api/about.html', {'title': 'About'})
