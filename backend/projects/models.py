from django.db import models
from django.conf import settings
from freelancers.models import Skill
from clients.models import ClientProfile


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open for Proposals'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    class ProjectType(models.TextChoices):
        SOLO = 'solo', 'Solo Freelancer'
        TEAM = 'team', 'Team / Squad'
        EITHER = 'either', 'Solo or Team'

    class Category(models.TextChoices):
        WEB = 'Web Development', 'Web Development'
        AI_ML = 'AI & Machine Learning', 'AI & Machine Learning'
        MOBILE = 'Mobile Apps', 'Mobile Apps'
        DESIGN = 'UI/UX & Design', 'UI/UX & Design'
        CLOUD = 'Cloud & DevOps', 'Cloud & DevOps'
        FULL_STACK = 'Full-Stack Product', 'Full-Stack Product'
        OTHER = 'Other', 'Other'

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed project requirements, goals, and deliverables")
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.FULL_STACK)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, default=ProjectType.EITHER)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    skills = models.ManyToManyField(Skill, through='ProjectSkill', related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def proposal_count(self):
        return self.proposals.count()


class ProjectSkill(models.Model):
    class RequiredLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_projects')
    required_level = models.CharField(max_length=20, choices=RequiredLevel.choices, default=RequiredLevel.ADVANCED)

    class Meta:
        unique_together = ('project', 'skill')

    def __str__(self):
        return f"{self.project.title} requires {self.skill.name}"


class ProjectAttachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='project_files/')
    name = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.file.name


class Milestone(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        FUNDED = 'funded', 'Funded (In Escrow)'
        IN_PROGRESS = 'in_progress', 'In Progress'
        SUBMITTED = 'submitted', 'Submitted for Review'
        APPROVED = 'approved', 'Approved & Released'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    contract = models.ForeignKey('proposals.Contract', on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=250.00)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f"{self.title} (${self.amount}) - {self.project.title}"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVIEW = 'review', 'In Review'
        DONE = 'done', 'Completed'

    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"
