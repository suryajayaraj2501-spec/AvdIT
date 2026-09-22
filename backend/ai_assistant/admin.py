from django.contrib import admin
from .models import AIConversation, AIMessage, AIRecommendation


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'title', 'updated_at', 'created_at']
    inlines = [AIMessageInline]


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'project', 'recommendation_type', 'created_at']
    list_filter = ['recommendation_type']
