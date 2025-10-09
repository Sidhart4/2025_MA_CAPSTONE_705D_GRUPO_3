# cuentas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
