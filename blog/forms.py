from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import Comment

class CommentForm(forms.Form):
	comment = forms.CharField(max_length=500, min_length=3, required=True)