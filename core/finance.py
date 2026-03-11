from django.db.models import Q
from django.utils import timezone

from .models import FinanceNotification


def publish_due_finance_notifications():
    now = timezone.now()
    due_notifications = FinanceNotification.objects.filter(sent_at__isnull=True).filter(
        Q(delivery_type='manual') | Q(delivery_type='automatic', scheduled_for__lte=now)
    )
    due_notifications.update(sent_at=now)
