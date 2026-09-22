from rest_framework import serializers
from .models import Service, ServicePackage, ServiceOrder
from freelancers.serializers import FreelancerProfileSerializer
from clients.serializers import ClientProfileSerializer


class ServicePackageSerializer(serializers.ModelSerializer):
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = ServicePackage
        fields = ['id', 'tier', 'tier_display', 'name', 'description', 'price', 'delivery_days', 'revisions', 'features']


class ServiceSerializer(serializers.ModelSerializer):
    freelancer = FreelancerProfileSerializer(read_only=True)
    starting_price = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = [
            'id', 'freelancer', 'title', 'category', 'description',
            'cover_image', 'is_active', 'rating', 'reviews_count',
            'orders_count', 'starting_price', 'created_at'
        ]


class ServiceDetailSerializer(ServiceSerializer):
    packages = ServicePackageSerializer(many=True, read_only=True)

    class Meta(ServiceSerializer.Meta):
        fields = ServiceSerializer.Meta.fields + ['packages']


class ServiceOrderSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    service_title = serializers.ReadOnlyField(source='service.title')
    package_name = serializers.ReadOnlyField(source='package.name')

    class Meta:
        model = ServiceOrder
        fields = ['id', 'service', 'service_title', 'package', 'package_name', 'client', 'requirements', 'status', 'total_price', 'created_at']
