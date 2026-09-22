from django.db import models
from freelancers.models import FreelancerProfile
from clients.models import ClientProfile


class Service(models.Model):
    class Category(models.TextChoices):
        WEB_DEV = 'Web Development', 'Web & Full-Stack Development'
        AI_SERVICES = 'AI & Machine Learning', 'AI Solutions & LLM Apps'
        UI_UX = 'UI/UX Design', 'UI/UX & Product Design'
        MOBILE_DEV = 'Mobile Apps', 'iOS & Android Development'
        DEVOPS_CLOUD = 'DevOps & Cloud', 'DevOps, Docker & Cloud'
        CONTENT_SEO = 'Content & SEO', 'Content, SEO & Copywriting'

    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=255, help_text="e.g., I will build a full-stack AI web application")
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.WEB_DEV)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    reviews_count = models.PositiveIntegerField(default=0)
    orders_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-orders_count', '-created_at']

    def __str__(self):
        return self.title

    @property
    def starting_price(self):
        basic_pkg = self.packages.filter(tier='basic').first()
        if basic_pkg:
            return basic_pkg.price
        first_pkg = self.packages.first()
        return first_pkg.price if first_pkg else 0


class ServicePackage(models.Model):
    class Tier(models.TextChoices):
        BASIC = 'basic', 'Basic'
        STANDARD = 'standard', 'Standard'
        PREMIUM = 'premium', 'Premium'

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='packages')
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BASIC)
    name = models.CharField(max_length=100, help_text="Package Name (e.g. Starter, Pro, Enterprise)")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.PositiveIntegerField(default=3)
    revisions = models.PositiveIntegerField(default=2)
    features = models.JSONField(default=list, blank=True, help_text="List of feature strings")

    class Meta:
        unique_together = ('service', 'tier')

    def __str__(self):
        return f"{self.service.title} - {self.get_tier_display()} (${self.price})"


class ServiceOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DELIVERED = 'delivered', 'Delivered'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='orders')
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='service_orders')
    requirements = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} for {self.service.title} by {self.client.user.display_name}"
