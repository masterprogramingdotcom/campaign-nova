from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from blog.models import Blog, Category, Comment


class CategoryListView(View):
    def get(self, request):
        categories = Category.objects.all().order_by("-id")
        return render(request, "home/category_list.html", {"categories": categories})


class BlogListView(View):
    def get(self, request):
        blogs = Blog.objects.select_related("category").all().order_by("-id")

        # Set up pagination
        paginator = Paginator(blogs, 6)  # Show 6 blogs per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "blog/blog-list.html", {"page_obj": page_obj})


class BlogDetailView(View):
    def get(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        comments = blog.comments.order_by("-created_at")
        comment_count = comments.count()
        return render(
            request,
            "blog/blog-details.html",
            {"blog": blog, "comments": comments, "comment_count": comment_count},
        )

    def post(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)

        # Capture form data
        text = request.POST.get("comment")

        # Save the new comment
        Comment.objects.create(
            blog=blog, user=request.user, text=text, created_at=timezone.now()
        )

        # Redirect to the same page to display the new comment
        return redirect("blog_detail", slug=slug)
