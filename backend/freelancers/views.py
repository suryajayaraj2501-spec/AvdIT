from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Skill, FreelancerProfile, FreelancerSkill, PortfolioItem, Experience
from .serializers import SkillSerializer, FreelancerProfileSerializer, FreelancerDetailSerializer, PortfolioItemSerializer
from accounts.permissions import IsFreelancer
from teams.models import Team


# ==========================================
# Server-Rendered Views
# ==========================================

def freelancer_list_view(request):
    query = request.GET.get('q', '')
    skill_filter = request.GET.get('skill', '')
    avail_filter = request.GET.get('availability', '')
    min_rating = request.GET.get('min_rating', '')

    freelancers = FreelancerProfile.objects.select_related('user').prefetch_related('freelancer_skills__skill').all()

    if query:
        freelancers = freelancers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(title__icontains=query) |
            Q(bio__icontains=query)
        )

    if skill_filter:
        freelancers = freelancers.filter(freelancer_skills__skill__name__iexact=skill_filter)

    if avail_filter:
        freelancers = freelancers.filter(availability=avail_filter)

    if min_rating:
        try:
            freelancers = freelancers.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    skills = Skill.objects.all()[:20]

    context = {
        'freelancers': freelancers,
        'skills': skills,
        'query': query,
        'selected_skill': skill_filter,
        'selected_avail': avail_filter,
    }
    return render(request, 'freelancer/freelancer_list.html', context)


def freelancer_detail_view(request, pk):
    freelancer = get_object_or_404(
        FreelancerProfile.objects.select_related('user').prefetch_related('freelancer_skills__skill', 'portfolio_items', 'experiences'),
        pk=pk
    )
    services = freelancer.services.filter(is_active=True)
    reviews = freelancer.user.received_reviews.all()[:10]
    
    return render(request, 'freelancer/freelancer_detail.html', {
        'freelancer': freelancer,
        'services': services,
        'reviews': reviews,
    })


def demo_showcase_view(request):
    """Gallery where Clients & Guests browse developers' & squads' demo projects."""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    filter_team = request.GET.get('type', '')

    demos = PortfolioItem.objects.select_related('freelancer__user', 'team').all()

    if query:
        demos = demos.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(freelancer__user__first_name__icontains=query) |
            Q(freelancer__user__last_name__icontains=query)
        )

    if category:
        demos = demos.filter(category=category)

    if filter_team == 'team':
        demos = demos.filter(team__isnull=False)
    elif filter_team == 'solo':
        demos = demos.filter(team__isnull=True)

    categories = ['Web Application', 'AI & Machine Learning', 'Mobile App', 'UI/UX Design', 'Cloud & DevOps']

    return render(request, 'freelancer/demo_showcase.html', {
        'demos': demos,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_type': filter_team,
    })


def demo_detail_view(request, pk):
    demo = get_object_or_404(
        PortfolioItem.objects.select_related('freelancer__user', 'team').prefetch_related('slides'),
        pk=pk
    )
    slides = demo.slides.all()
    return render(request, 'freelancer/demo_detail.html', {
        'demo': demo,
        'slides': slides
    })


@login_required
def my_demos_view(request):
    """Developer's private demo management view - ONLY shows that developer's projects."""
    profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    my_demos = PortfolioItem.objects.filter(freelancer=profile).select_related('team').prefetch_related('slides')
    user_teams = Team.objects.filter(members__user=request.user)

    return render(request, 'freelancer/my_demos.html', {
        'profile': profile,
        'my_demos': my_demos,
        'user_teams': user_teams,
    })


@login_required
def upload_demo_view(request):
    """Developer upload demo project flow with slide deck presentations."""
    profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    user_teams = Team.objects.filter(members__user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'Web Application')
        description = request.POST.get('description', '').strip()
        project_url = request.POST.get('project_url', '').strip()
        github_url = request.POST.get('github_url', '').strip()
        tags = request.POST.get('tags', '').strip()
        team_id = request.POST.get('team_id')
        image = request.FILES.get('image')
        slides_files = request.FILES.getlist('slides')

        if not title:
            messages.error(request, "Project title is required.")
            return render(request, 'freelancer/upload_demo.html', {'user_teams': user_teams})

        # If no main cover image was uploaded, use the first slide as cover
        if not image and slides_files:
            image = slides_files[0]

        team = None
        if team_id:
            team = Team.objects.filter(id=team_id, members__user=request.user).first()

        demo = PortfolioItem.objects.create(
            freelancer=profile,
            team=team,
            title=title,
            category=category,
            description=description,
            project_url=project_url,
            github_url=github_url,
            tags=tags,
            image=image
        )

        # Save slides
        for idx, s_file in enumerate(slides_files):
            caption_key = f"caption_{idx}"
            caption = request.POST.get(caption_key, f"Slide {idx + 1}").strip()
            PortfolioSlide.objects.create(
                portfolio_item=demo,
                image=s_file,
                caption=caption if caption else f"Slide {idx + 1}",
                order=idx
            )

        messages.success(request, f"Demo project '{demo.title}' with {len(slides_files) if slides_files else (1 if image else 0)} slide(s) uploaded successfully!")
        return redirect('freelancers:my_demos')

    return render(request, 'freelancer/upload_demo.html', {'user_teams': user_teams})


@login_required
def delete_demo_view(request, pk):
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    demo = get_object_or_404(PortfolioItem, pk=pk, freelancer=profile)
    title = demo.title
    demo.delete()
    messages.info(request, f"Demo project '{title}' removed.")
    return redirect('freelancers:my_demos')



@login_required
def freelancer_dashboard_view(request):
    profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    
    # Active proposals & contracts
    from proposals.models import Proposal, Contract
    from services.models import ServiceOrder
    
    proposals = Proposal.objects.filter(freelancer=profile).order_by('-created_at')[:5]
    active_contracts = Contract.objects.filter(freelancer=profile, status=Contract.Status.ACTIVE)
    completed_contracts = Contract.objects.filter(freelancer=profile, status=Contract.Status.COMPLETED)
    recent_orders = ServiceOrder.objects.filter(service__freelancer=profile).order_by('-created_at')[:5]
    my_demos = profile.portfolio_items.all()
    my_teams = Team.objects.filter(members__user=request.user)

    # Earnings calculation
    total_earned = Contract.objects.filter(freelancer=profile, status=Contract.Status.COMPLETED).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    profile.total_earnings = total_earned
    profile.completed_projects_count = completed_contracts.count()
    profile.save(update_fields=['total_earnings', 'completed_projects_count'])

    return render(request, 'freelancer/dashboard.html', {
        'profile': profile,
        'proposals': proposals,
        'active_contracts': active_contracts,
        'completed_contracts_count': completed_contracts.count(),
        'recent_orders': recent_orders,
        'my_demos': my_demos,
        'my_teams': my_teams,
    })


@login_required
def my_freelancer_profile_view(request):
    profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        profile.title = request.POST.get('title', profile.title)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.hourly_rate = request.POST.get('hourly_rate', profile.hourly_rate)
        profile.availability = request.POST.get('availability', profile.availability)
        profile.experience_level = request.POST.get('experience_level', profile.experience_level)
        profile.location = request.POST.get('location', profile.location)
        profile.save()

        # Handle skill updates
        skill_ids = request.POST.getlist('skills')
        if skill_ids:
            FreelancerSkill.objects.filter(freelancer=profile).delete()
            for s_id in skill_ids:
                try:
                    s_obj = Skill.objects.get(id=s_id)
                    FreelancerSkill.objects.create(freelancer=profile, skill=s_obj)
                except Skill.DoesNotExist:
                    pass

        messages.success(request, "Freelancer profile updated successfully.")
        return redirect('freelancers:my_profile')

    return render(request, 'freelancer/profile_edit.html', {
        'profile': profile,
        'all_skills': all_skills,
    })


# ==========================================
# REST API Endpoints
# ==========================================

class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']


class FreelancerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FreelancerProfile.objects.select_related('user').prefetch_related('freelancer_skills__skill', 'portfolio_items', 'experiences').all()
    serializer_class = FreelancerDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'title', 'bio', 'freelancer_skills__skill__name']


class FreelancerEarningsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsFreelancer]

    def get(self, request):
        profile = get_object_or_404(FreelancerProfile, user=request.user)
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        earnings = [450, 780, 1200, 950, 1600, 2100, 1850, float(profile.total_earnings) or 2400]

        return Response({
            'total_earnings': profile.total_earnings,
            'completed_projects': profile.completed_projects_count,
            'rating': profile.rating,
            'chart_labels': months,
            'chart_data': earnings
        })
