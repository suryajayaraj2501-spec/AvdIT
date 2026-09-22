from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'type_display', 'title', 'message', 'link', 'is_read', 'created_at', 'formatted_date']

    def get_formatted_date(self, obj):
        return obj.created_at.strftime('%b %d, %H:%M')
