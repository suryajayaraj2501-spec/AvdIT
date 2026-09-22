from django.contrib import admin
from .models import Proposal, Contract


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['project', 'freelancer', 'team', 'bid_amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['project__title', 'freelancer__user__username', 'team__name']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'client', 'freelancer', 'team', 'total_amount', 'status', 'start_date']
    list_filter = ['status']
    search_fields = ['project__title', 'client__user__username']
