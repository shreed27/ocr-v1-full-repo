from django import forms
from common.forms import AjaxForm

"""
class MultiChoicesField(AutoSelect2MultipleField):
    def validate_value(self, value):
        return True

    def coerce_value(self, value):
        return int(value)

    def get_val_txt(self, value):
        return self.big_data.get(value, None)

    def get_results(self, request, term, page, context):
        return (NO_ERR_RESP, False, term)
    """


class OptionDetailForm(AjaxForm):
    year = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}))
    level = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}))
    subject = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}))

    def clean_year(self):
        years = self.cleaned_data['year'].strip('[]').split(',')
        return [year.strip('""') for year in years]

    def clean_level(self):
        levels = self.cleaned_data['level'].strip('[]').split(',')
        return [level.strip('""') for level in levels]

    def clean_subject(self):
        subjects = self.cleaned_data['subject'].strip('[]').split(',')
        return [subject.strip('""') for subject in subjects]
