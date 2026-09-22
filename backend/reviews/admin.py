from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'rating', 'target_type', 'project', 'created_at']
    list_filter = ['rating', 'target_type']
    search_fields = ['reviewer__username', 'reviewee__username', 'comment']
