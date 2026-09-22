from rest_framework import serializers
from .models import Skill, FreelancerProfile, FreelancerSkill, PortfolioItem, Experience
from accounts.serializers import UserSummarySerializer


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'icon']


class FreelancerSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')
    skill_category = serializers.ReadOnlyField(source='skill.category')
    skill_icon = serializers.ReadOnlyField(source='skill.icon')

    class Meta:
        model = FreelancerSkill
        fields = ['id', 'skill', 'skill_name', 'skill_category', 'skill_icon', 'proficiency', 'years_of_experience']


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'description', 'image', 'project_url', 'created_at']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company', 'role', 'start_date', 'end_date', 'is_current', 'description']


class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    skills_list = FreelancerSkillSerializer(source='freelancer_skills', many=True, read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = [
            'id', 'user', 'title', 'bio', 'hourly_rate', 'availability',
            'experience_level', 'location', 'rating', 'total_reviews_count',
            'completed_projects_count', 'total_earnings', 'skills_list', 'created_at'
        ]


class FreelancerDetailSerializer(FreelancerProfileSerializer):
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)

    class Meta(FreelancerProfileSerializer.Meta):
        fields = FreelancerProfileSerializer.Meta.fields + ['portfolio_items', 'experiences']
