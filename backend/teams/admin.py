from django.contrib import admin
from .models import Team, TeamMember, TeamSkill, TeamInvitation


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1


class TeamSkillInline(admin.TabularInline):
    model = TeamSkill
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'hourly_rate', 'is_available', 'rating', 'completed_projects_count']
    list_filter = ['is_available', 'rating']
    search_fields = ['name', 'tagline', 'created_by__username']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TeamMemberInline, TeamSkillInline]


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ['team', 'invited_user', 'role_in_team', 'status', 'created_at']
    list_filter = ['status']
