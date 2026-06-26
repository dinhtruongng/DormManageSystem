from django import forms

from dorm_system.common.models import Audience


class AnnouncementForm(forms.Form):
    title = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4})
    )
    audience = forms.ChoiceField(
        choices=Audience.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
        initial=Audience.ALL,
    )
