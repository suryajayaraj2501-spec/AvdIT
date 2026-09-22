from rest_framework import serializers
from .models import Proposal, Contract
from projects.serializers import ProjectSerializer
from freelancers.serializers import FreelancerProfileSerializer
from teams.serializers import TeamSerializer
from clients.serializers import ClientProfileSerializer


class ProposalSerializer(serializers.ModelSerializer):
    project_title = serializers.ReadOnlyField(source='project.title')
    applicant_name = serializers.ReadOnlyField()

    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'project_title', 'freelancer', 'team',
            'applicant_name', 'bid_amount', 'cover_letter',
            'estimated_duration_days', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']


class ContractSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    client = ClientProfileSerializer(read_only=True)
    freelancer = FreelancerProfileSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'proposal', 'project', 'client', 'freelancer', 'team',
            'total_amount', 'start_date', 'end_date', 'status', 'created_at'
        ]
