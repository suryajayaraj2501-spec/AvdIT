from django.db import models
from django.conf import settings
from django.db.models import Avg


class ClientProfile(models.Model):
    class CompanySize(models.TextChoices):
        SOLO = '1', 'Individual / 1 person'
        SMALL = '2-10', 'Small (2-10 employees)'
        MEDIUM = '11-50', 'Medium (11-50 employees)'
        LARGE = '51-200', 'Mid-Large (51-200 employees)'
        ENTERPRISE = '200+', 'Enterprise (200+ employees)'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=150, blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='Technology')
    company_size = models.CharField(max_length=20, choices=CompanySize.choices, default=CompanySize.SMALL)
    company_website = models.URLField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    about_company = models.TextField(blank=True, default='')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    hire_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    reviews_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name or self.user.display_name} (Client)"

    def update_rating(self):
        from reviews.models import Review
        avg = Review.objects.filter(reviewee=self.user).aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            self.rating = round(avg, 2)
            self.reviews_count = Review.objects.filter(reviewee=self.user).count()
            self.save(update_fields=['rating', 'reviews_count'])
