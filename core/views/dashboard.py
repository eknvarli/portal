from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Project, Payment, Proposal, ServiceRequest

@login_required
def index(request):
    projects = request.user.projects.all().order_by('-updated_at', '-created_at')
    selected_project_id = request.GET.get('project')

    if selected_project_id:
        current_project = projects.filter(pk=selected_project_id).first()
    else:
        current_project = projects.first()
    
    payments = []
    proposals = []
    service_requests = []
    project_documents_count = 0
    project_request_count = 0
    
    if current_project:
        payments = current_project.payments.all().order_by('due_date')
        proposals = current_project.proposals.filter(status='Pending')
        service_requests = current_project.service_requests.all()[:5]
        project_documents_count = current_project.documents.count()
        project_request_count = current_project.service_requests.count()

    context = {
        'projects': projects,
        'project': current_project,
        'payments': payments,
        'proposals': proposals,
        'service_requests': service_requests,
        'project_documents_count': project_documents_count,
        'project_request_count': project_request_count,
    }
    return render(request, 'core/index.html', context)
