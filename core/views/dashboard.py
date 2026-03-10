from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Project, Payment, Proposal

@login_required
def index(request):
    # Fetch projects for the logged-in client
    projects = request.user.projects.all()
    # For now, let's take the latest project if multiple exist
    current_project = projects.first()
    
    payments = []
    proposals = []
    
    if current_project:
        payments = current_project.payments.all().order_by('due_date')
        proposals = current_project.proposals.filter(status='Pending')

    context = {
        'project': current_project,
        'payments': payments,
        'proposals': proposals,
    }
    return render(request, 'core/index.html', context)
