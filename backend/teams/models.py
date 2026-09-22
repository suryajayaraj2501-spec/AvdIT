from django.db import models
from django.conf import settings
from django.utils.text import slugify
from freelancers.models import Skill


class Team(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, default='High-performance multidisciplinary squad')
    description = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='teams/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_teams')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=120.00, help_text="Combined estimated hourly rate")
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    reviews_count = models.PositiveIntegerField(default=0)
    completed_projects_count = models.PositiveIntegerField(default=0)
    skills = models.ManyToManyField(Skill, through='TeamSkill', related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-completed_projects_count', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class TeamMember(models.Model):
    class TeamRole(models.TextChoices):
        LEAD = 'Team Lead', 'Team Lead'
        UI_UX = 'UI/UX Designer', 'UI/UX Designer'
        FRONTEND = 'Frontend Developer', 'Frontend Developer'
        BACKEND = 'Backend Developer', 'Backend Developer'
        FULLSTACK = 'Full-Stack Developer', 'Full-Stack Developer'
        AI_DEV = 'AI / ML Engineer', 'AI / ML Engineer'
        MOBILE_DEV = 'Mobile Developer', 'Mobile Developer'
        DEVOPS = 'DevOps Engineer', 'DevOps Engineer'
        QA = 'QA & Tester', 'QA & Tester'
        MEMBER = 'Specialist / Contributor', 'Specialist / Contributor'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    role_in_team = models.CharField(max_length=50, default=TeamRole.MEMBER)
    is_lead = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.display_name} in {self.team.name} ({self.role_in_team})"


class TeamSkill(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_teams')

    class Meta:
        unique_together = ('team', 'skill')

    def __str__(self):
        return f"{self.team.name} - {self.skill.name}"


class TeamInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_team_invitations')
    role_in_team = models.CharField(max_length=50, default='Specialist / Contributor')
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite for {self.invited_user.username} to join {self.team.name}"
