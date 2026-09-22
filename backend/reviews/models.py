from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from projects.models import Project
from services.models import ServiceOrder


class Review(models.Model):
    class TargetType(models.TextChoices):
        FREELANCER = 'freelancer', 'Freelancer'
        TEAM = 'team', 'Team'
        CLIENT = 'client', 'Client'

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    target_type = models.CharField(max_length=20, choices=TargetType.choices, default=TargetType.FREELANCER)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5 stars"
    )
    comment = models.TextField(help_text="Detailed client or freelancer feedback")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ Review from {self.reviewer.username} to {self.reviewee.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically update reviewee profile ratings
        if hasattr(self.reviewee, 'freelancer_profile'):
            self.reviewee.freelancer_profile.update_rating()
        if hasattr(self.reviewee, 'client_profile'):
            self.reviewee.client_profile.update_rating()
