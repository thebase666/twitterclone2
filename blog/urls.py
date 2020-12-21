from django.urls import path, include
from .views import (PostListView, PostDetailView, PostCreateView, PostUpdateView,
                    PostDeleteView, UserPostListView, FollowsListView, FollowersListView, postpreference)
from .import views

urlpatterns = [
    path('about/', views.about, name='blog-about'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/del/', PostDeleteView.as_view(), name='post-delete'),
    path('user/<str:username>/follows', FollowsListView.as_view(), name='user-follows'),
    path('user/<str:username>/followers', FollowersListView.as_view(), name='user-followers'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:postid>/preference/<int:userpreference>', postpreference, name='postpreference'),  # 点赞 写的不太对
]