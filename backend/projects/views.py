from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Project, ProjectSkill, ProjectAttachment, Milestone, Task
from .serializers import ProjectSerializer, ProjectDetailSerializer, MilestoneSerializer, TaskSerializer
from clients.models import ClientProfile
from freelancers.models import Skill, FreelancerProfile
from teams.models import Team
from proposals.models import Proposal, Contract


# ==========================================
# Server-Rendered Views
# ==========================================

def project_list_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    p_type = request.GET.get('type', '')
    skill_filter = request.GET.get('skill', '')

    projects = Project.objects.filter(status=Project.Status.OPEN).select_related('client__user').prefetch_related('project_skills__skill')

    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        projects = projects.filter(category=category)

    if p_type:
        projects = projects.filter(project_type=p_type)

    if skill_filter:
        projects = projects.filter(project_skills__skill__name__iexact=skill_filter)

    categories = Project.Category.choices
    skills = Skill.objects.all()[:20]

    return render(request, 'project/project_list.html', {
        'projects': projects,
        'categories': categories,
        'skills': skills,
        'query': query,
        'selected_category': category,
        'selected_type': p_type,
    })


def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('client__user').prefetch_related('project_skills__skill', 'attachments', 'milestones'),
        pk=pk
    )

    has_applied = False
    freelancer_teams = []
    if request.user.is_authenticated and request.user.is_freelancer:
        fl_profile = getattr(request.user, 'freelancer_profile', None)
        if fl_profile:
            has_applied = Proposal.objects.filter(project=project, freelancer=fl_profile).exists()
            freelancer_teams = Team.objects.filter(members__user=request.user)

    is_owner = request.user.is_authenticated and (hasattr(request.user, 'client_profile') and project.client == request.user.client_profile)

    return render(request, 'project/project_detail.html', {
        'project': project,
        'has_applied': has_applied,
        'freelancer_teams': freelancer_teams,
        'is_owner': is_owner,
    })


@login_required
def project_create_view(request):
    client_profile, _ = ClientProfile.objects.get_or_create(user=request.user)
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', Project.Category.FULL_STACK)
        project_type = request.POST.get('project_type', Project.ProjectType.EITHER)
        budget = request.POST.get('budget', 1000)
        deadline = request.POST.get('deadline') or None

        if not title or not description:
            messages.error(request, "Title and description are required.")
            return render(request, 'project/project_create.html', {'skills': all_skills, 'categories': Project.Category.choices})

        project = Project.objects.create(
            client=client_profile,
            title=title,
            description=description,
            category=category,
            project_type=project_type,
            budget=budget,
            deadline=deadline,
            status=Project.Status.OPEN
        )

        # Attach skills
        skill_ids = request.POST.getlist('skills')
        for s_id in skill_ids:
            try:
                skill_obj = Skill.objects.get(id=s_id)
                ProjectSkill.objects.create(project=project, skill=skill_obj)
            except Skill.DoesNotExist:
                pass

        # Handle attachment
        if 'attachment' in request.FILES:
            ProjectAttachment.objects.create(
                project=project,
                file=request.FILES['attachment'],
                name=request.FILES['attachment'].name
            )

        messages.success(request, "Project posted successfully! Check out AI matching recommendations.")
        return redirect('projects:detail', pk=project.id)

    return render(request, 'project/project_create.html', {
        'skills': all_skills,
        'categories': Project.Category.choices,
        'types': Project.ProjectType.choices
    })


@login_required
def project_workspace_view(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('milestones__tasks__assignee', 'attachments'),
        pk=pk
    )

    # Verify user is client, assigned freelancer, or team member
    is_client = hasattr(request.user, 'client_profile') and project.client == request.user.client_profile
    active_contract = Contract.objects.filter(project=project).first()

    is_authorized = is_client or (
        active_contract and (
            (active_contract.freelancer and active_contract.freelancer.user == request.user) or
            (active_contract.team and active_contract.team.members.filter(user=request.user).exists())
        )
    ) or request.user.is_staff

    if not is_authorized and not is_client:
        messages.error(request, "You do not have access to this workspace.")
        return redirect('projects:detail', pk=pk)

    milestones = project.milestones.all()
    tasks = Task.objects.filter(milestone__project=project)
    
    # Calculate progress %
    total_milestones = milestones.count()
    completed_milestones = milestones.filter(status=Milestone.Status.APPROVED).count()
    progress_pct = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0

    return render(request, 'project/workspace.html', {
        'project': project,
        'contract': active_contract,
        'milestones': milestones,
        'tasks': tasks,
        'progress_pct': progress_pct,
        'is_client': is_client,
    })


@login_required
def add_milestone_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', 100)
        due_date = request.POST.get('due_date') or None

        contract = Contract.objects.filter(project=project).first()
        Milestone.objects.create(
            project=project,
            contract=contract,
            title=title,
            description=description,
            amount=amount,
            due_date=due_date,
            status=Milestone.Status.PENDING
        )
        messages.success(request, f"Milestone '{title}' added.")
    return redirect('projects:workspace', pk=project_id)


@login_required
def add_task_view(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        due_date = request.POST.get('due_date') or None
        Task.objects.create(
            milestone=milestone,
            title=title,
            description=description,
            assignee=request.user,
            due_date=due_date
        )
        messages.success(request, f"Task '{title}' created.")
    return redirect('projects:workspace', pk=milestone.project.id)


@login_required
def update_task_status_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW, Task.Status.DONE]:
            task.status = new_status
            task.save()
            messages.success(request, f"Task updated to {task.get_status_display()}.")
    return redirect('projects:workspace', pk=task.milestone.project.id)


# ==========================================
# REST API ViewSets
# ==========================================

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('client__user').prefetch_related('project_skills__skill', 'attachments').all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category', 'project_skills__skill__name']


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
