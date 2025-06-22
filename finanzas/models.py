from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

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
    ultima_actualizacion = models.DateField(default=timezone.now)

    def calcular_cuota(self):
        """Calcula la cuota periódica del préstamo respetando que el plazo se
        almacena en meses."""

        if self.frecuencia_pago == 'mensual':
            num_pagos = self.plazo
            tasa_periodica = self.tasa_anual / 100 / 12
        else:
            num_pagos = ceil(self.plazo * 52 / 12)
            tasa_periodica = self.tasa_anual / 100 / 52

        if tasa_periodica == 0:
            return self.monto / num_pagos

        cuota = (self.monto * tasa_periodica * (1 + tasa_periodica) ** num_pagos) / (
            (1 + tasa_periodica) ** num_pagos - 1)
        return round(cuota, 2)

    def saldo_actual(self):
        total_incrementos = sum(i.monto for i in self.incrementos.all())
        total_pagos = sum(p.monto for p in self.pagos.all())
        return self.monto + total_incrementos - total_pagos

    def calcular_interes_periodico(self, cuota_esperada):
        tasa_periodica = self.tasa_anual / (100 * (12 if self.frecuencia_pago == 'mensual' else 52))
        return round(cuota_esperada * tasa_periodica, 2)

    def __str__(self):
        return f"Préstamo de {self.nombre_cliente}"


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
    extender_plazo = models.BooleanField(default=False)
    nuevo_plazo = models.IntegerField(null=True, blank=True)
    meses_adicionales = models.IntegerField(null=True, blank=True)  # Permitir valores nulos temporalmente

    def save(self, *args, **kwargs):
        if self.meses_adicionales is None:
            self.meses_adicionales = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Incremento de ${self.monto} para {self.prestamo}"



class Inversion(models.Model):
    nombre = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    tasa_anual = models.DecimalField(max_digits=5, decimal_places=2)
    plazo = models.IntegerField()  # en meses

    def __str__(self):
        return f"Inversión de {self.nombre} - ${self.monto}"


class GestorSaldo:
    @staticmethod
    def actualizar_saldos():
        hoy = timezone.now().date()
        prestamos = Prestamo.objects.all()

        for prestamo in prestamos:
            dias_transcurridos = (hoy - prestamo.fecha_inicio).days
            dias_por_periodo = 30 if prestamo.frecuencia_pago == 'mensual' else 8
            periodos_transcurridos = dias_transcurridos // dias_por_periodo

            for periodo in range(1, periodos_transcurridos + 1):
                fecha_periodo = prestamo.fecha_inicio + timedelta(days=periodo * dias_por_periodo)

                # Ya se capitalizó este periodo
                if prestamo.incrementos.filter(fecha=fecha_periodo).exists():
                    continue

                # Total pagado en el periodo
                fecha_inicio_periodo = fecha_periodo - timedelta(days=dias_por_periodo)
                pagos = prestamo.pagos.filter(fecha_pago__range=(fecha_inicio_periodo, fecha_periodo))
                total_pagado = sum(p.monto for p in pagos)

                cuota_periodica = prestamo.calcular_cuota()

                if total_pagado < cuota_periodica:
                    interes = prestamo.calcular_interes_periodico(cuota_periodica)
                    IncrementoPrestamo.objects.create(
                        prestamo=prestamo,
                        monto=interes,
                        fecha=fecha_periodo,
                        extender_plazo=False  # Agregado el campo requerido
                    )
