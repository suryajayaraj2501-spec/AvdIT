from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Type(models.TextChoices):
        MESSAGE = 'message', 'New Message'
        PROPOSAL = 'proposal', 'Proposal Update'
        CONTRACT = 'contract', 'Contract Milestone'
        PAYMENT = 'payment', 'Payment Notification'
        TEAM_INVITE = 'team_invite', 'Team Invitation'
        SYSTEM = 'system', 'System Alert'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, default='#')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    @classmethod
    def send(cls, user, notification_type, title, message, link='#'):
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
