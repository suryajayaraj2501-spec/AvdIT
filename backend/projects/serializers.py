from rest_framework import serializers
from .models import Project, ProjectSkill, ProjectAttachment, Milestone, Task
from clients.serializers import ClientProfileSerializer
from accounts.serializers import UserSummarySerializer


class ProjectSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')
    skill_icon = serializers.ReadOnlyField(source='skill.icon')

    class Meta:
        model = ProjectSkill
        fields = ['id', 'skill', 'skill_name', 'skill_icon', 'required_level']


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAttachment
        fields = ['id', 'file', 'name', 'uploaded_at']


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSummarySerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['id', 'milestone', 'title', 'description', 'assignee', 'assignee_id', 'status', 'due_date', 'created_at']


class MilestoneSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Milestone
        fields = ['id', 'project', 'contract', 'title', 'description', 'amount', 'due_date', 'status', 'tasks', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    skills_list = ProjectSkillSerializer(source='project_skills', many=True, read_only=True)
    proposal_count = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'client', 'title', 'description', 'category', 'project_type',
            'budget', 'budget_max', 'deadline', 'status', 'skills_list',
            'proposal_count', 'created_at', 'updated_at'
        ]


class ProjectDetailSerializer(ProjectSerializer):
    attachments = ProjectAttachmentSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['attachments', 'milestones']
