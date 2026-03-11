from .finance import publish_due_finance_notifications
from .models import Announcement


def announcements(request):
    if not request.user.is_authenticated:
        return {'sidebar_announcements': []}

    publish_due_finance_notifications()

    return {
        'sidebar_announcements': Announcement.objects.select_related('created_by')[:5],
    }
