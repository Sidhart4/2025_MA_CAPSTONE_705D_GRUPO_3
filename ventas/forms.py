from django import forms


class CheckoutForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre y apellido",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre de quien paga"}),
    )
    rut = forms.CharField(
        label="RUT / DNI",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "11.111.111-1"}),
    )
    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"placeholder": "tucorreo@email.com"}),
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "+56 9 1234 5678"}),
    )
    comentarios = forms.CharField(
        label="Notas para recepción",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Instrucciones para cuando retire la compra...",
            }
        ),
    )
