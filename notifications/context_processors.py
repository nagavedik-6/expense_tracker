from .models import Notification


def unread_notifications_count(request):
    """Context processor to inject unread notification count."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent = Notification.objects.filter(user=request.user, is_read=False)[:5]
        return {
            'unread_notifications_count': count,
            'recent_notifications': recent,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }
