from django.urls import path

from blog.views import BlogDetailView, BlogListView, CategoryListView

urlpatterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    path("<str:slug>/", BlogDetailView.as_view(), name="blog_detail"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
]
