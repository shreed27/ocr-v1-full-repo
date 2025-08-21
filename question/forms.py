from django import forms


class QuestionVideoForm(forms.Form):
    videoupload = forms.FileField()