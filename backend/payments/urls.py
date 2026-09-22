from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Server-rendered templates
    path('history/', views.payment_history_view, name='history'),

    # REST API endpoints
    path('create-order/', views.CreateRazorpayOrderAPIView.as_view(), name='api_create_order'),
    path('verify-signature/', views.VerifyPaymentSignatureAPIView.as_view(), name='api_verify_signature'),
    path('release-milestone/<int:milestone_id>/', views.ReleaseMilestoneEscrowAPIView.as_view(), name='api_release_milestone'),
]
