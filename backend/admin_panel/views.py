from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.models import User
from projects.models import Project
from proposals.models import Contract
from teams.models import Team
from services.models import Service, ServiceOrder
from payments.models import Payment, Transaction


def is_staff_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.role == User.Role.ADMIN or user.is_superuser)


@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def admin_dashboard_view(request):
    total_users = User.objects.count()
    clients_count = User.objects.filter(role=User.Role.CLIENT).count()
    freelancers_count = User.objects.filter(role=User.Role.FREELANCER).count()
    total_teams = Team.objects.count()
    total_projects = Project.objects.count()
    active_contracts = Contract.objects.filter(status=Contract.Status.ACTIVE).count()

    total_volume = Payment.objects.filter(status__in=[Payment.Status.ESCROW_FUNDED, Payment.Status.RELEASED]).aggregate(Sum('amount'))['amount__sum'] or 0
    in_escrow = Payment.objects.filter(status=Payment.Status.ESCROW_FUNDED).aggregate(Sum('amount'))['amount__sum'] or 0
    platform_revenue = round(float(total_volume) * 0.10, 2)  # 10% platform fee simulation

    recent_users = User.objects.order_by('-created_at')[:8]
    recent_projects = Project.objects.order_by('-created_at')[:6]
    recent_payments = Payment.objects.order_by('-created_at')[:6]

    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'clients_count': clients_count,
        'freelancers_count': freelancers_count,
        'total_teams': total_teams,
        'total_projects': total_projects,
        'active_contracts': active_contracts,
        'total_volume': total_volume,
        'in_escrow': in_escrow,
        'platform_revenue': platform_revenue,
        'recent_users': recent_users,
        'recent_projects': recent_projects,
        'recent_payments': recent_payments,
    })


@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def admin_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def admin_projects_view(request):
    projects = Project.objects.select_related('client__user').order_by('-created_at')
    contracts = Contract.objects.select_related('project', 'client__user').order_by('-created_at')
    return render(request, 'admin_panel/projects.html', {'projects': projects, 'contracts': contracts})


# ==========================================
# REST API Endpoint for Chart.js
# ==========================================

class AdminStatsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        volume_data = [12500, 18200, 24000, 31500, 42000, 56000, 68000, 84500]

        clients_count = User.objects.filter(role=User.Role.CLIENT).count()
        freelancers_count = User.objects.filter(role=User.Role.FREELANCER).count()
        admins_count = User.objects.filter(role=User.Role.ADMIN).count() or 1

        return Response({
            'months': months,
            'volume_data': volume_data,
            'user_distribution_labels': ['Clients', 'Freelancers', 'Staff'],
            'user_distribution_data': [clients_count or 12, freelancers_count or 28, admins_count]
        })
