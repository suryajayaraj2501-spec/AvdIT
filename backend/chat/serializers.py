from rest_framework import serializers
from .models import Conversation, Message
from accounts.serializers import UserSummarySerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.display_name')
    sender_avatar = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'sender_avatar', 'content', 'attachment', 'attachment_url', 'is_read', 'timestamp', 'formatted_time']

    def get_sender_avatar(self, obj):
        return obj.sender.avatar.url if obj.sender.avatar else None

    def get_attachment_url(self, obj):
        return obj.attachment.url if obj.attachment else None

    def get_formatted_time(self, obj):
        return obj.timestamp.strftime('%H:%M | %b %d')


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSummarySerializer(many=True, read_only=True)
    latest_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'related_project', 'latest_message', 'unread_count', 'updated_at', 'created_at']

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
