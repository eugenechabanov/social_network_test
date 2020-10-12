from django.urls import path
from .views import (
    CreatePostAPIView,
    ListAllAPIView,
    LikePostAPIView,
    UnlikePostAPIView,
    DeletePostAPIView,
    FilterPostsByDateAPIView,
    LikesFilteredByDateAPIView,
    LikesAggregatedByDaysAPIView,
    UserStatsAPIView,
    UserCreate,
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView)

urlpatterns = [
    # ============ API ==============
    path('api/list_all', ListAllAPIView.as_view()),
    path('api/create_post', CreatePostAPIView.as_view()),
    path('api/delete/<int:id>', DeletePostAPIView.as_view()),
    path('api/like/<int:post_id>', LikePostAPIView.as_view()),
    path('api/unlike/<int:post_id>', LikePostAPIView.as_view()),
    path('api/filter_posts_by_date', FilterPostsByDateAPIView.as_view()),
    path('api/likes_filtered_by_date', LikesFilteredByDateAPIView.as_view()),
    path('api/likes_aggregated_by_days', LikesAggregatedByDaysAPIView.as_view()),
    path('api/user_stats', UserStatsAPIView.as_view()),
    path('user/register', UserCreate.as_view()),

    # ============ Front-End Views =============
    path('', PostListView.as_view(), name='home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
]