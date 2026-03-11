from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import ServiceRequestForm


@login_required
def create_service_request(request):
    selected_project_id = request.GET.get('project')
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES, user=request.user, selected_project_id=selected_project_id)
        if form.is_valid():
            form.save()
            messages.success(request, 'Talebiniz basariyla gonderildi.')
            return redirect('index')
    else:
        form = ServiceRequestForm(user=request.user, selected_project_id=selected_project_id)

    return render(request, 'core/create_service_request.html', {'form': form})