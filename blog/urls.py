from django.urls import path

from .views import BlogDetailView, BlogListView

urlpatterns = [
    path("blog/", BlogListView.as_view(), name="blog_list"),
    path("blog/<int:pk>/", BlogDetailView.as_view(), name="blog_detail"),
]
