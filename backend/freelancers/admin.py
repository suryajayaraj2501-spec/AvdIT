from django.contrib import admin
from .models import Skill, FreelancerProfile, FreelancerSkill, PortfolioItem, Experience


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icon']
    list_filter = ['category']
    search_fields = ['name']


class FreelancerSkillInline(admin.TabularInline):
    model = FreelancerSkill
    extra = 1


class PortfolioItemInline(admin.StackedInline):
    model = PortfolioItem
    extra = 0


class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'hourly_rate', 'availability', 'experience_level', 'rating', 'completed_projects_count']
    list_filter = ['availability', 'experience_level', 'rating']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'title']
    inlines = [FreelancerSkillInline, PortfolioItemInline, ExperienceInline]
