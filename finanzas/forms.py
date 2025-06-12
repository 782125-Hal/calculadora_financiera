from django import forms
from .models import Prestamo, Pago

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Prestamo

class PrestamoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de préstamos.
    Incluye validaciones personalizadas y widgets específicos para cada campo.
    """
    # Constantes de clase
    MONTO_MIN = 100
    MONTO_MAX = 1000000
    TASA_MIN = 0.01
    TASA_MAX = 100
    PLAZO_MIN = 1
    PLAZO_MAX = 360

    # Redefinición de campos con validaciones específicas
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(MONTO_MIN),
            MaxValueValidator(MONTO_MAX)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el monto del préstamo'
        })
    )

    tasa_interes = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(TASA_MIN),
            MaxValueValidator(TASA_MAX)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la tasa de interés'
        })
    )

    plazo = forms.IntegerField(
        validators=[
            MinValueValidator(PLAZO_MIN),
            MaxValueValidator(PLAZO_MAX)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el plazo en meses'
        })
    )

    class Meta:
        model = Prestamo
        fields = ['nombre_cliente', 'monto', 'tasa_anual', 'plazo', 'fecha_inicio']
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
        fields = ['monto', 'fecha_pago']  # Asegúrate de usar solo los campos que existen en el modelo Pago
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

# Si necesitas un formulario para incremento de préstamo
class IncrementoPrestamoForm(forms.Form):
    monto_incremento = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Monto del incremento'
    )
