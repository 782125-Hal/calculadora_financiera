from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Prestamo, Pago

class PrestamoForm(forms.ModelForm):
    """
    Formulario para registrar préstamos basado en cálculo previo.
    Solo solicita nombre y fecha, el resto se oculta y se llena desde la sesión.
    """

    MONTO_MIN = 100
    MONTO_MAX = 1000000
    TASA_MIN = 0.01
    TASA_MAX = 100
    PLAZO_MIN = 1
    PLAZO_MAX = 360

    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(MONTO_MIN),
            MaxValueValidator(MONTO_MAX)
        ],
        widget=forms.HiddenInput()
    )

    tasa_anual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(TASA_MIN),
            MaxValueValidator(TASA_MAX)
        ],
        widget=forms.HiddenInput()
    )

    plazo = forms.IntegerField(
        validators=[
            MinValueValidator(PLAZO_MIN),
            MaxValueValidator(PLAZO_MAX)
        ],
        widget=forms.HiddenInput()
    )

    frecuencia_pago = forms.ChoiceField(
        choices=[('mensual', 'Mensual'), ('semanal', 'Semanal')],
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Prestamo
        fields = ['nombre_cliente', 'fecha_inicio', 'monto', 'tasa_anual', 'plazo', 'frecuencia_pago']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'fecha_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
        }

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'fecha_pago']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

class IncrementoPrestamoForm(forms.Form):
    monto_incremento = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Monto del incremento'
    )
