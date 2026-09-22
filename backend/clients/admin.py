from django.contrib import admin
from .models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'industry', 'company_size', 'total_spent', 'hire_count', 'rating']
    list_filter = ['industry', 'company_size', 'rating']
    search_fields = ['company_name', 'user__username', 'user__email']
