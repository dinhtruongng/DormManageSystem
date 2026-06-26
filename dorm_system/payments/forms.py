from django import forms


class PaymentUploadForm(forms.Form):
    amount = forms.DecimalField(
        min_value=0, decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    evidence = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.pdf"}
        ),
    )
