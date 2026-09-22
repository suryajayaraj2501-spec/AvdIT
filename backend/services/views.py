from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from .models import Service, ServicePackage, ServiceOrder
from .serializers import ServiceSerializer, ServiceDetailSerializer, ServiceOrderSerializer
from freelancers.models import FreelancerProfile
from clients.models import ClientProfile


# ==========================================
# Server-Rendered Views
# ==========================================

def service_list_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '-rating')

    services = Service.objects.filter(is_active=True).select_related('freelancer__user').prefetch_related('packages')

    if query:
        services = services.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(freelancer__user__first_name__icontains=query) |
            Q(freelancer__user__last_name__icontains=query)
        )

    if category:
        services = services.filter(category=category)

    if sort_by in ['-rating', 'rating', '-created_at', 'created_at']:
        services = services.order_by(sort_by)

    categories = Service.Category.choices

    return render(request, 'service/service_list.html', {
        'services': services,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'sort_by': sort_by,
    })


def service_detail_view(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('freelancer__user').prefetch_related('packages'),
        pk=pk
    )
    packages = service.packages.all()
    basic_pkg = packages.filter(tier=ServicePackage.Tier.BASIC).first()
    standard_pkg = packages.filter(tier=ServicePackage.Tier.STANDARD).first()
    premium_pkg = packages.filter(tier=ServicePackage.Tier.PREMIUM).first()

    reviews = service.freelancer.user.received_reviews.all()[:6]

    return render(request, 'service/service_detail.html', {
        'service': service,
        'basic_pkg': basic_pkg,
        'standard_pkg': standard_pkg,
        'premium_pkg': premium_pkg,
        'reviews': reviews,
    })


@login_required
def service_create_view(request):
    freelancer_profile, _ = FreelancerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', Service.Category.WEB_DEV)
        description = request.POST.get('description', '').strip()
        cover_image = request.FILES.get('cover_image')

        if not title or not description:
            messages.error(request, "Service title and description are required.")
            return render(request, 'service/service_create.html', {'categories': Service.Category.choices})

        service = Service.objects.create(
            freelancer=freelancer_profile,
            title=title,
            category=category,
            description=description,
            cover_image=cover_image
        )

        # Create Basic Package
        ServicePackage.objects.create(
            service=service,
            tier=ServicePackage.Tier.BASIC,
            name=request.POST.get('basic_name', 'Starter Package'),
            description=request.POST.get('basic_desc', 'Basic tier deliverables'),
            price=request.POST.get('basic_price', 50),
            delivery_days=request.POST.get('basic_days', 3),
            revisions=request.POST.get('basic_revs', 1),
            features=[f.strip() for f in request.POST.get('basic_features', '').split(',') if f.strip()]
        )

        # Create Standard Package
        ServicePackage.objects.create(
            service=service,
            tier=ServicePackage.Tier.STANDARD,
            name=request.POST.get('std_name', 'Standard Package'),
            description=request.POST.get('std_desc', 'Standard comprehensive delivery'),
            price=request.POST.get('std_price', 150),
            delivery_days=request.POST.get('std_days', 7),
            revisions=request.POST.get('std_revs', 3),
            features=[f.strip() for f in request.POST.get('std_features', '').split(',') if f.strip()]
        )

        # Create Premium Package
        ServicePackage.objects.create(
            service=service,
            tier=ServicePackage.Tier.PREMIUM,
            name=request.POST.get('prem_name', 'Premium AI Pro Package'),
            description=request.POST.get('prem_desc', 'Full enterprise-level delivery'),
            price=request.POST.get('prem_price', 350),
            delivery_days=request.POST.get('prem_days', 14),
            revisions=request.POST.get('prem_revs', 5),
            features=[f.strip() for f in request.POST.get('prem_features', '').split(',') if f.strip()]
        )

        messages.success(request, f"Service '{service.title}' published successfully!")
        return redirect('services:detail', pk=service.id)

    return render(request, 'service/service_create.html', {'categories': Service.Category.choices})


@login_required
def service_checkout_view(request, package_id):
    package = get_object_or_404(ServicePackage.objects.select_related('service__freelancer__user'), pk=package_id)
    client_profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        requirements = request.POST.get('requirements', '')
        
        order = ServiceOrder.objects.create(
            service=package.service,
            package=package,
            client=client_profile,
            requirements=requirements,
            total_price=package.price,
            status=ServiceOrder.Status.PENDING
        )

        package.service.orders_count += 1
        package.service.save(update_fields=['orders_count'])

        return render(request, 'service/checkout_success.html', {
            'order': order,
            'package': package,
        })

    return render(request, 'service/checkout.html', {
        'package': package,
        'service': package.service,
    })


# ==========================================
# REST API ViewSet
# ==========================================

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True).select_related('freelancer__user').prefetch_related('packages')
    serializer_class = ServiceDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category']
