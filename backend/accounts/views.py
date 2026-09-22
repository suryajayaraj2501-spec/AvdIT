from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import User
from .forms import AdvITRegistrationForm, AdvITLoginForm, UserProfileUpdateForm
from .serializers import UserSerializer, UserSummarySerializer, RegisterSerializer
from .permissions import IsOwnerOrReadOnly


# ==========================================
# Server-Rendered Template Views
# ==========================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = AdvITRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure appropriate profile creation
            if user.role == User.Role.FREELANCER:
                from freelancers.models import FreelancerProfile
                FreelancerProfile.objects.get_or_create(user=user)
            elif user.role == User.Role.CLIENT:
                from clients.models import ClientProfile
                ClientProfile.objects.get_or_create(user=user)
            
            login(request, user)
            messages.success(request, f"Welcome to AdvIT, {user.display_name}! Your account is ready.")
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        role_param = request.GET.get('role', User.Role.FREELANCER)
        initial_role = role_param if role_param in [User.Role.FREELANCER, User.Role.CLIENT] else User.Role.FREELANCER
        form = AdvITRegistrationForm(initial={'role': initial_role})

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = AdvITLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.display_name}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AdvITLoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('landing:index')


@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_staff or user.role == User.Role.ADMIN:
        return redirect('admin_panel:dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('clients:dashboard')
    else:
        return redirect('freelancers:dashboard')


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile_edit')
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, 'auth/profile_edit.html', {'form': form})


# ==========================================
# REST Framework API Views
# ==========================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSummarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user.role == User.Role.FREELANCER:
                from freelancers.models import FreelancerProfile
                FreelancerProfile.objects.get_or_create(user=user)
            elif user.role == User.Role.CLIENT:
                from clients.models import ClientProfile
                ClientProfile.objects.get_or_create(user=user)

            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
