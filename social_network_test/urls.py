from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users import views as user_views
from api.views import CustomTokenObtainPairView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    # path('api/token', TokenObtainPairView.as_view()),
    path('api/token', CustomTokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),

    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]
