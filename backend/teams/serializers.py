from rest_framework import serializers
from .models import Team, TeamMember, TeamSkill, TeamInvitation
from accounts.serializers import UserSummarySerializer
from freelancers.serializers import SkillSerializer


class TeamSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')
    skill_icon = serializers.ReadOnlyField(source='skill.icon')

    class Meta:
        model = TeamSkill
        fields = ['id', 'skill', 'skill_name', 'skill_icon']


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role_in_team', 'is_lead', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    skills_list = TeamSkillSerializer(source='team_skills', many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'slug', 'tagline', 'description', 'avatar',
            'created_by', 'hourly_rate', 'is_available', 'rating',
            'reviews_count', 'completed_projects_count', 'member_count',
            'skills_list', 'created_at'
        ]


class TeamDetailSerializer(TeamSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ['members']


class TeamInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    invited_user_name = serializers.ReadOnlyField(source='invited_user.display_name')

    class Meta:
        model = TeamInvitation
        fields = ['id', 'team', 'team_name', 'invited_user', 'invited_user_name', 'role_in_team', 'message', 'status', 'created_at']
