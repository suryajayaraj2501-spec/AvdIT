from django.db import models
from django.conf import settings
from projects.models import Project
from freelancers.models import FreelancerProfile
from clients.models import ClientProfile
from teams.models import Team


class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='proposals')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='proposals')
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    cover_letter = models.TextField()
    estimated_duration_days = models.PositiveIntegerField(default=14)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        applicant = self.freelancer.user.display_name if self.freelancer else (self.team.name if self.team else 'Unknown')
        return f"Proposal by {applicant} for {self.project.title} (${self.bid_amount})"

    @property
    def applicant_name(self):
        if self.freelancer:
            return self.freelancer.user.display_name
        elif self.team:
            return f"Team {self.team.name}"
        return "Unknown"

    @property
    def applicant_user(self):
        if self.freelancer:
            return self.freelancer.user
        elif self.team:
            return self.team.created_by
        return None


class Contract(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        DISPUTED = 'disputed', 'In Dispute'
        TERMINATED = 'terminated', 'Terminated'

    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='contract')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contracts')
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='contracts')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract #{self.id} - {self.project.title} (${self.total_amount})"
