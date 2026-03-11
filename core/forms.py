from pathlib import Path

from django import forms

from .models import Comment, CustomUser, Project, ServiceRequest, ServiceRequestAttachment


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            if self.required:
                raise forms.ValidationError('En az bir dosya yuklemelisiniz.')
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []
        errors = []

        for item in data:
            try:
                cleaned_files.append(super().clean(item, initial))
            except forms.ValidationError as error:
                errors.extend(error.error_list)

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_files

class CustomerLoginForm(forms.Form):
    customer_number = forms.CharField(
        label='Musteri Numarasi',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Musteri numaranizi girin'}),
    )

    error_messages = {
        'invalid_login': 'Bu musteri numarasi ile eslesen aktif bir hesap bulunamadi.',
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_customer_number(self):
        customer_number = self.cleaned_data['customer_number'].strip()
        try:
            self.user_cache = CustomUser.objects.get(customer_number=customer_number, is_active=True)
        except CustomUser.DoesNotExist as error:
            raise forms.ValidationError(self.error_messages['invalid_login']) from error
        return customer_number

    def get_user(self):
        return self.user_cache

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Yorumunuzu buraya yazın...', 'rows': 3}),
        }


class ServiceRequestForm(forms.ModelForm):
    project_choice = forms.ChoiceField(label='Proje', choices=())
    attachments = MultipleFileField(
        label='Talep Dosyalari',
        required=True,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': '.png,.jpg,.jpeg,.webp'}),
    )

    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'budget', 'urgency']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Talep adini girin'}),
            'description': forms.Textarea(attrs={'placeholder': 'Talep aciklamasini yazin', 'rows': 6}),
            'budget': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'urgency': forms.Select(),
        }
        labels = {
            'title': 'Talep Adi',
            'description': 'Talep Aciklamasi',
            'budget': 'Talep Butcesi',
            'urgency': 'Talep Aciliyeti',
        }

    def __init__(self, *args, user=None, selected_project_id=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        project_choices = [('new', 'Yeni Proje')]
        if self.user is not None:
            user_projects = self.user.projects.order_by('name')
            project_choices.extend((str(project.pk), project.name) for project in user_projects)
            default_project = 'new' if not user_projects.exists() else str(user_projects.first().pk)
            if selected_project_id and user_projects.filter(pk=selected_project_id).exists():
                default_project = str(selected_project_id)
            self.fields['project_choice'].initial = default_project
        else:
            self.fields['project_choice'].initial = 'new'
        self.fields['project_choice'].choices = project_choices

    def clean_attachments(self):
        files = self.cleaned_data['attachments']
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}

        for uploaded_file in files:
            extension = Path(uploaded_file.name).suffix.lower()
            if extension not in allowed_extensions:
                raise forms.ValidationError('Sadece png, jpg, jpeg ve webp dosyalari yukleyebilirsiniz.')

        return files

    def save(self):
        project_choice = self.cleaned_data['project_choice']
        if project_choice == 'new':
            project = Project.objects.create(
                name=f"Yeni Proje - {self.cleaned_data['title']}",
                status='Talep Alindi',
                progress=0,
                client=self.user,
            )
        else:
            project = self.user.projects.get(pk=project_choice)

        service_request = ServiceRequest.objects.create(
            project=project,
            requester=self.user,
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            budget=self.cleaned_data['budget'],
            urgency=self.cleaned_data['urgency'],
        )

        attachments = [
            ServiceRequestAttachment(service_request=service_request, file=uploaded_file)
            for uploaded_file in self.cleaned_data['attachments']
        ]
        ServiceRequestAttachment.objects.bulk_create(attachments)

        return service_request
