from django.db import models
from django.conf import settings
from projects.models import Project


class AIConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_conversations')
    session_id = models.CharField(max_length=100, blank=True, default='')
    title = models.CharField(max_length=200, default='AdvIT AI Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        user_label = self.user.username if self.user else f"Guest ({self.session_id[:8]})"
        return f"AI Chat with {user_label} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class AIMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'AI Assistant'
        SYSTEM = 'system', 'System'

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    content = models.TextField()
    structured_data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."


class AIRecommendation(models.Model):
    class RecType(models.TextChoices):
        TEAM_STRUCTURE = 'team_structure', 'Team Structure & Roles'
        FREELANCER_MATCH = 'freelancer_match', 'Freelancer / Team Match'
        PROPOSAL_DRAFT = 'proposal_draft', 'Proposal Cover Letter Draft'
        PROFILE_TIP = 'profile_tip', 'Profile Enhancement Tip'
        PROJECT_MILESTONES = 'project_milestones', 'Project Milestones Breakdown'

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_recommendations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=40, choices=RecType.choices, default=RecType.TEAM_STRUCTURE)
    payload = models.JSONField(default=dict, help_text="AI generated structured JSON output")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Rec ({self.get_recommendation_type_display()}) at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
