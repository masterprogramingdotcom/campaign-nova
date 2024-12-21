from django.contrib import admin

from blog.models import Blog, Category, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)  # Filter by creation date
    ordering = ("-created_at",)  # Order by creation date descending


class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "created_at")
    search_fields = ("title", "content", "tags")
    list_filter = (
        "user",
        "category",
        "created_at",
    )  # Filter by user, category, and creation date
    ordering = ("-created_at",)  # Order by creation date descending


class CommentAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "created_at")
    search_fields = ("text",)
    list_filter = ("user", "created_at")  # Filter by user and creation date
    ordering = ("-created_at",)  # Order by creation date descending


# Register your models with the admin site
admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
