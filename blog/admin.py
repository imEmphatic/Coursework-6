from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'views_count')
    list_filter = ('pub_date', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('views_count',)