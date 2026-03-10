from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Document, Comment
from ..forms import CommentForm

@login_required
def file_center(request):
    projects = request.user.projects.all()
    documents = Document.objects.filter(project__in=projects).prefetch_related('comments')
    
    if request.method == 'POST':
        doc_id = request.POST.get('document_id')
        document = get_object_or_404(Document, id=doc_id, project__client=request.user)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            comment.save()
            return redirect('file_center')
    else:
        form = CommentForm()

    return render(request, 'core/file_center.html', {
        'documents': documents,
        'comment_form': form,
    })
