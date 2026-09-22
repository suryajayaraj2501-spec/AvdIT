from django.contrib import admin
from .models import Service, ServicePackage, ServiceOrder


class ServicePackageInline(admin.TabularInline):
    model = ServicePackage
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'freelancer', 'category', 'rating', 'orders_count', 'is_active']
    list_filter = ['category', 'is_active', 'rating']
    search_fields = ['title', 'freelancer__user__username']
    inlines = [ServicePackageInline]


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'package', 'client', 'total_price', 'status', 'created_at']
    list_filter = ['status']
