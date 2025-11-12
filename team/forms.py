from django import forms
from .models import PlayerApplication, NewsComment


class JoinForm(forms.ModelForm):
    class Meta:
        model = PlayerApplication
        fields = ['name', 'age', 'position', 'experience', 'phone', 'email']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 4}),
        }


class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['author_name', 'email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Оставьте ваш комментарий...'
            }),
            'author_name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email (необязательно)'
            }),
        }
