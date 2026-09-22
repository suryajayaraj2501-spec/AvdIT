from rest_framework import serializers
from .models import ClientProfile
from accounts.serializers import UserSummarySerializer


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'company_name', 'industry', 'company_size',
            'company_website', 'location', 'about_company', 'total_spent',
            'hire_count', 'rating', 'reviews_count', 'created_at'
        ]
