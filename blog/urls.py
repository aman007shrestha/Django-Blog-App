
from django.urls import path
from . import views
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView, 
    PostDeleteView, 
    UserPostListView,
    )

urlpatterns = [
    path('', PostListView.as_view(), name="blog-home"),
    path('post/<int:pk>/', PostDetailView.as_view(), name="post-detail"),
    path('about/', views.about, name="blog-about"),
    path('post/new/', PostCreateView.as_view(), name="post-create"),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name="post-update"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="post-delete"),
    path('post/<int:pk>/comment', views.CommentCreateView.as_view(), name="post-comment-create"),
    path('post/<int:pk>/comment/delete', views.CommentDeleteView.as_view(), name='post-comment-delete'),
    path('post/<int:pk>/like', views.PostLikeView.as_view(), name="post-like"),
    path('post/<int:pk>/unlike', views.DeleteLikeView.as_view(), name="post-unlike"),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
]
