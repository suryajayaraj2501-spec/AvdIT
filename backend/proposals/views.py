from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Proposal, Contract
from .serializers import ProposalSerializer, ContractSerializer
from projects.models import Project, Milestone
from freelancers.models import FreelancerProfile
from teams.models import Team
from notifications.models import Notification


# ==========================================
# Server-Rendered Views
# ==========================================

@login_required
def submit_proposal_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, status=Project.Status.OPEN)

    if hasattr(request.user, 'client_profile') and project.client == request.user.client_profile:
        messages.error(request, "You cannot apply to your own project.")
        return redirect('projects:detail', pk=project_id)

    freelancer_profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    user_teams = Team.objects.filter(members__user=request.user)

    if request.method == 'POST':
        apply_as = request.POST.get('apply_as', 'solo')
        bid_amount = request.POST.get('bid_amount', project.budget)
        cover_letter = request.POST.get('cover_letter', '').strip()
        duration = request.POST.get('estimated_duration_days', 14)

        if not cover_letter:
            messages.error(request, "Cover letter is required.")
            return render(request, 'proposal/submit_proposal.html', {'project': project, 'user_teams': user_teams})

        proposal_kwargs = {
            'project': project,
            'bid_amount': bid_amount,
            'cover_letter': cover_letter,
            'estimated_duration_days': duration,
        }

        if apply_as == 'team':
            team_id = request.POST.get('team_id')
            selected_team = get_object_or_404(Team, id=team_id)
            proposal_kwargs['team'] = selected_team
        else:
            proposal_kwargs['freelancer'] = freelancer_profile

        proposal = Proposal.objects.create(**proposal_kwargs)

        # Notify Client
        Notification.send(
            user=project.client.user,
            notification_type=Notification.Type.PROPOSAL,
            title=f"New proposal for {project.title}",
            message=f"{proposal.applicant_name} submitted a bid of ${proposal.bid_amount}.",
            link=f"/projects/{project.id}/"
        )

        messages.success(request, "Proposal submitted successfully! You will be notified when the client responds.")
        return redirect('proposals:my_proposals')

    return render(request, 'proposal/submit_proposal.html', {
        'project': project,
        'user_teams': user_teams,
        'freelancer': freelancer_profile,
    })


@login_required
def my_proposals_view(request):
    freelancer_profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    proposals = Proposal.objects.filter(freelancer=freelancer_profile).select_related('project__client__user')
    team_proposals = Proposal.objects.filter(team__members__user=request.user).select_related('project__client__user')

    return render(request, 'proposal/my_proposals.html', {
        'proposals': proposals,
        'team_proposals': team_proposals,
    })


@login_required
def accept_proposal_view(request, proposal_id):
    proposal = get_object_or_404(Proposal.objects.select_related('project__client__user'), id=proposal_id)
    project = proposal.project

    if not (hasattr(request.user, 'client_profile') and project.client == request.user.client_profile):
        messages.error(request, "Only the project owner can accept this proposal.")
        return redirect('projects:detail', pk=project.id)

    if request.method == 'POST':
        # Accept proposal
        proposal.status = Proposal.Status.ACCEPTED
        proposal.save()

        # Reject all other pending proposals for this project
        Proposal.objects.filter(project=project).exclude(id=proposal.id).update(status=Proposal.Status.REJECTED)

        # Update project status
        project.status = Project.Status.IN_PROGRESS
        project.save(update_fields=['status'])

        # Auto-create contract
        contract, created = Contract.objects.get_or_create(
            proposal=proposal,
            defaults={
                'project': project,
                'client': project.client,
                'freelancer': proposal.freelancer,
                'team': proposal.team,
                'total_amount': proposal.bid_amount,
                'status': Contract.Status.ACTIVE
            }
        )

        # Auto-create initial milestone if none exists
        if not project.milestones.exists():
            Milestone.objects.create(
                project=project,
                contract=contract,
                title="Milestone 1: Project Setup & Core Deliverable",
                description="Initial delivery phase as outlined in proposal scope.",
                amount=proposal.bid_amount,
                status=Milestone.Status.PENDING
            )

        # Notify Freelancer / Team
        recipient_user = proposal.applicant_user
        if recipient_user:
            Notification.send(
                user=recipient_user,
                notification_type=Notification.Type.CONTRACT,
                title=f"Proposal Accepted! Contract started for {project.title}",
                message=f"Congratulations! {project.client.user.display_name} has accepted your proposal.",
                link=f"/projects/{project.id}/workspace/"
            )

        messages.success(request, f"Proposal accepted! Contract #{contract.id} created and workspace initialized.")
        return redirect('projects:workspace', pk=project.id)

    return redirect('projects:detail', pk=project.id)


@login_required
def reject_proposal_view(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    project = proposal.project

    if hasattr(request.user, 'client_profile') and project.client == request.user.client_profile:
        proposal.status = Proposal.Status.REJECTED
        proposal.save()
        messages.info(request, "Proposal marked as rejected.")

    return redirect('projects:detail', pk=project.id)


# ==========================================
# REST API ViewSets
# ==========================================

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
