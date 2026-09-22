from rest_framework import serializers
from .models import Review
from accounts.serializers import UserSummarySerializer


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSummarySerializer(read_only=True)
    reviewee = UserSummarySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewee', 'target_type', 'project', 'service_order', 'rating', 'comment', 'created_at']
