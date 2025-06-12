


from django.db import models
from django.utils import timezone
from math import log, ceil

class Prestamo(models.Model):
    FRECUENCIA_CHOICES = [
        ('mensual', 'Mensual'),
        ('semanal', 'Semanal'),
    ]

    nombre_cliente = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    plazo = models.IntegerField(help_text="Plazo en meses")
    tasa_anual = models.DecimalField(max_digits=5, decimal_places=2)
    frecuencia_pago = models.CharField(max_length=10, choices=FRECUENCIA_CHOICES, default='mensual')
    fecha_inicio = models.DateField(default=timezone.now)

    def calcular_cuota(self):
        tasa_periodica = self.tasa_anual / (100 * (12 if self.frecuencia_pago == 'mensual' else 52))
        num_pagos = self.plazo * (12 if self.frecuencia_pago == 'mensual' else 52)

        if tasa_periodica == 0:
            return self.monto / num_pagos

        cuota = (self.monto * tasa_periodica * (1 + tasa_periodica) ** num_pagos) / (
                (1 + tasa_periodica) ** num_pagos - 1)
        return round(cuota, 2)

    def saldo_actual(self):
        pagos = self.pagos.all()
        incrementos = self.incrementos.all()

        # Suma todos los incrementos
        total_incrementos = sum(incremento.monto for incremento in incrementos)
        # Suma todos los pagos
        total_pagos = sum(pago.monto for pago in pagos)  # Cambiado de monto_pagado a monto

        return self.monto + total_incrementos - total_pagos

    def format_monto(self, valor):
        """Formatea un valor monetario con el símbolo de moneda y separadores de miles."""
        return f'${valor:,.2f}'

    def __str__(self):
        """Devuelve una representación en cadena del préstamo con el monto formateado."""
        return f"Préstamo de {self.nombre_cliente} - {self.format_monto(self.monto)}"



class Pago(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Pago de ${self.monto} para préstamo {self.prestamo.id}"


class IncrementoPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='incrementos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    nuevo_plazo = models.IntegerField(help_text="Nuevo plazo en meses", null=True, blank=True)

    def __str__(self):
        return f"Incremento de ${self.monto} para {self.prestamo.nombre_cliente}"


from django.db import models


class Inversion(models.Model):
    nombre = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    tasa_anual = models.DecimalField(max_digits=5, decimal_places=2)
    plazo = models.IntegerField()  # en meses

    def __str__(self):
        return f"Inversión de {self.nombre} - ${self.monto}"
