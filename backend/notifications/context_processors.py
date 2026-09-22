def unread_notifications(request):
    """Context processor to provide unread notification count across all templates."""
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            count = Notification.objects.filter(user=request.user, is_read=False).count()
            recent = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
            return {'unread_notifications_count': count, 'recent_notifications': recent}
        except Exception:
            return {'unread_notifications_count': 0, 'recent_notifications': []}
    return {'unread_notifications_count': 0, 'recent_notifications': []}
