from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..finance import publish_due_finance_notifications
from ..models import BankInformation, FinanceNotification


@login_required
def finance_overview(request):
    publish_due_finance_notifications()
    bank_information = BankInformation.objects.first()
    finance_notifications = FinanceNotification.objects.filter(
        user=request.user,
        sent_at__isnull=False,
    ).order_by('-sent_at', '-created_at')

    context = {
        'bank_information': bank_information,
        'finance_notifications': finance_notifications,
    }
    return render(request, 'core/finance.html', context)