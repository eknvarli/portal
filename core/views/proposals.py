from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Proposal

@login_required
def approve_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id, project__client=request.user)
    proposal.status = 'Approved'
    proposal.approved_at = timezone.now()
    proposal.save()
    return redirect('index')
