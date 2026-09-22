from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from .models import Team, TeamMember, TeamSkill, TeamInvitation
from .serializers import TeamSerializer, TeamDetailSerializer, TeamInvitationSerializer
from freelancers.models import Skill
from accounts.models import User


# ==========================================
# Server-Rendered Views
# ==========================================

def team_list_view(request):
    query = request.GET.get('q', '')
    skill_filter = request.GET.get('skill', '')
    avail_filter = request.GET.get('availability', '')

    teams = Team.objects.prefetch_related('members__user', 'team_skills__skill').all()

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(tagline__icontains=query) |
            Q(description__icontains=query)
        )

    if skill_filter:
        teams = teams.filter(team_skills__skill__name__iexact=skill_filter)

    if avail_filter == 'available':
        teams = teams.filter(is_available=True)

    skills = Skill.objects.all()[:20]

    return render(request, 'team/team_list.html', {
        'teams': teams,
        'skills': skills,
        'query': query,
        'selected_skill': skill_filter,
    })


def team_detail_view(request, slug):
    team = get_object_or_404(
        Team.objects.prefetch_related('members__user', 'team_skills__skill'),
        slug=slug
    )
    is_member = False
    is_lead = False
    if request.user.is_authenticated:
        is_member = team.members.filter(user=request.user).exists()
        is_lead = (team.created_by == request.user)

    available_freelancers = []
    if is_lead:
        # Get users who are not yet members to invite
        member_ids = team.members.values_list('user_id', flat=True)
        available_freelancers = User.objects.filter(role=User.Role.FREELANCER).exclude(id__in=member_ids)[:20]

    return render(request, 'team/team_detail.html', {
        'team': team,
        'is_member': is_member,
        'is_lead': is_lead,
        'available_freelancers': available_freelancers,
    })


@login_required
def create_team_view(request):
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tagline = request.POST.get('tagline', '').strip()
        description = request.POST.get('description', '').strip()
        hourly_rate = request.POST.get('hourly_rate', 120)
        avatar = request.FILES.get('avatar')

        if not name:
            messages.error(request, "Team name is required.")
            return render(request, 'team/create_team.html', {'all_skills': all_skills})

        team = Team.objects.create(
            name=name,
            tagline=tagline,
            description=description,
            hourly_rate=hourly_rate,
            avatar=avatar,
            created_by=request.user
        )

        # Add creator as Team Lead
        TeamMember.objects.create(
            team=team,
            user=request.user,
            role_in_team=TeamMember.TeamRole.LEAD,
            is_lead=True
        )

        # Add skills
        skill_ids = request.POST.getlist('skills')
        for s_id in skill_ids:
            try:
                skill_obj = Skill.objects.get(id=s_id)
                TeamSkill.objects.create(team=team, skill=skill_obj)
            except Skill.DoesNotExist:
                pass

        messages.success(request, f"Team '{team.name}' has been created! You can now invite members.")
        return redirect('teams:detail', slug=team.slug)

    return render(request, 'team/create_team.html', {'all_skills': all_skills})


@login_required
def my_teams_view(request):
    owned_teams = Team.objects.filter(created_by=request.user)
    member_teams = Team.objects.filter(members__user=request.user).exclude(created_by=request.user)
    invitations = TeamInvitation.objects.filter(invited_user=request.user, status=TeamInvitation.Status.PENDING)

    return render(request, 'team/my_teams.html', {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
        'invitations': invitations,
    })


@login_required
def invite_member_view(request, team_id):
    team = get_object_or_404(Team, id=team_id, created_by=request.user)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_in_team = request.POST.get('role_in_team', 'Specialist / Contributor')
        message_text = request.POST.get('message', '')

        try:
            invited_user = User.objects.get(id=user_id)
            if not team.members.filter(user=invited_user).exists():
                TeamInvitation.objects.create(
                    team=team,
                    invited_user=invited_user,
                    role_in_team=role_in_team,
                    message=message_text
                )
                from notifications.models import Notification
                Notification.send(
                    user=invited_user,
                    notification_type=Notification.Type.TEAM_INVITE,
                    title=f"Invitation to join squad {team.name}",
                    message=f"{request.user.display_name} invited you to join '{team.name}' as a {role_in_team}.",
                    link='/teams/my-teams/'
                )
                messages.success(request, f"Invitation sent to {invited_user.display_name}.")
            else:
                messages.warning(request, "User is already a member of this team.")
        except User.DoesNotExist:
            messages.error(request, "Selected user was not found.")

    return redirect('teams:detail', slug=team.slug)


@login_required
def respond_invitation_view(request, invite_id, action):
    invite = get_object_or_404(TeamInvitation, id=invite_id, invited_user=request.user, status=TeamInvitation.Status.PENDING)

    if action == 'accept':
        invite.status = TeamInvitation.Status.ACCEPTED
        invite.save()
        TeamMember.objects.get_or_create(
            team=invite.team,
            user=request.user,
            defaults={'role_in_team': invite.role_in_team}
        )
        messages.success(request, f"You have joined {invite.team.name}!")
    elif action == 'decline':
        invite.status = TeamInvitation.Status.DECLINED
        invite.save()
        messages.info(request, "Invitation declined.")

    return redirect('teams:my_teams')


# ==========================================
# REST API ViewSet
# ==========================================

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.prefetch_related('members__user', 'team_skills__skill').all()
    serializer_class = TeamDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'tagline', 'description', 'team_skills__skill__name']
