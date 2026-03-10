from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Comment

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label="Müşteri Numarası", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Müşteri Numaranızı Girin'}))
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Şifreniz'}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Yorumunuzu buraya yazın...', 'rows': 3}),
        }
