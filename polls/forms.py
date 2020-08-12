from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Comment

import datetime

field_required = 'Это поле обязательно'
field_not_required = 'Это поле не обязательно'


class QuestionForm(forms.Form):
    question_text = forms.CharField(max_length=200)


class ChoiceForm(forms.Form):
    choice_text = forms.CharField(max_length=200)


class AuthorForm(forms.ModelForm):
    birth_date = forms.DateField(required=False)
    min = "1900-01-01"
    max = timezone.now().strftime('%Y-%m-%d')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birth_date')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment_text', 'rel_comment')


class SignUpForm(AuthorForm, UserCreationForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise ValidationError(f'User with email {email} already exists!')
        return email

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'birth_date', 'password1', 'password2')