from django.db import models
from django.conf import settings
from django.db.models import Avg


class Skill(models.Model):
    class Category(models.TextChoices):
        DEVELOPMENT = 'Development', 'Software & Web Development'
        AI_DATA = 'AI & Data', 'AI, ML & Data Science'
        DESIGN = 'Design', 'Design & Creative'
        MOBILE = 'Mobile', 'Mobile App Development'
        DEVOPS = 'DevOps', 'DevOps & Cloud'
        MARKETING = 'Marketing', 'Marketing & Writing'
        OTHER = 'Other', 'Other'

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.DEVELOPMENT)
    icon = models.CharField(max_length=50, blank=True, default='bi-code-slash')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FreelancerProfile(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available for Work'
        BUSY = 'busy', 'Partially Available'
        NOT_AVAILABLE = 'not_available', 'Not Available'

    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', 'Entry Level (1-2 yrs)'
        INTERMEDIATE = 'intermediate', 'Intermediate (3-5 yrs)'
        EXPERT = 'expert', 'Expert (5+ yrs)'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_profile')
    title = models.CharField(max_length=150, blank=True, default='Professional Freelancer')
    bio = models.TextField(blank=True, default='')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=35.00)
    availability = models.CharField(max_length=20, choices=Availability.choices, default=Availability.AVAILABLE)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.INTERMEDIATE)
    location = models.CharField(max_length=100, blank=True, default='')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_reviews_count = models.PositiveIntegerField(default=0)
    completed_projects_count = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    skills = models.ManyToManyField(Skill, through='FreelancerSkill', related_name='freelancers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.display_name} - {self.title}"

    def update_rating(self):
        from reviews.models import Review
        avg = Review.objects.filter(reviewee=self.user).aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            self.rating = round(avg, 2)
            self.total_reviews_count = Review.objects.filter(reviewee=self.user).count()
            self.save(update_fields=['rating', 'total_reviews_count'])


class FreelancerSkill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='freelancer_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_freelancers')
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices, default=Proficiency.ADVANCED)
    years_of_experience = models.PositiveIntegerField(default=2)

    class Meta:
        unique_together = ('freelancer', 'skill')

    def __str__(self):
        return f"{self.freelancer.user.username} - {self.skill.name} ({self.proficiency})"


class PortfolioItem(models.Model):
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='portfolio_items')
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='demo_projects')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default='Web Application')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    project_url = models.URLField(blank=True, default='', help_text="Live demo or website URL")
    github_url = models.URLField(blank=True, default='', help_text="GitHub repository URL")
    tags = models.CharField(max_length=255, blank=True, default='', help_text="e.g. Django, React, Google Gemini API")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.freelancer.user.username}"

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class PortfolioSlide(models.Model):
    portfolio_item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE, related_name='slides')
    image = models.ImageField(upload_to='portfolio/slides/')
    caption = models.CharField(max_length=200, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Slide {self.order + 1} for {self.portfolio_item.title}"


class Experience(models.Model):
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.role} at {self.company}"
