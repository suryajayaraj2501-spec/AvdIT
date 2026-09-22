from django.contrib import admin
from .models import Project, ProjectSkill, ProjectAttachment, Milestone, Task


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 1


class ProjectAttachmentInline(admin.TabularInline):
    model = ProjectAttachment
    extra = 0


class MilestoneInline(admin.StackedInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'category', 'project_type', 'budget', 'status', 'created_at']
    list_filter = ['category', 'project_type', 'status']
    search_fields = ['title', 'description', 'client__user__username']
    inlines = [ProjectSkillInline, ProjectAttachmentInline, MilestoneInline]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'amount', 'due_date', 'status']
    list_filter = ['status']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'milestone', 'assignee', 'status', 'due_date']
    list_filter = ['status']
