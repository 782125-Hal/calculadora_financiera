from django.test import TestCase
from .models import Prestamo


class PrestamoCalculoTest(TestCase):
    def test_calcular_cuota_mensual(self):
        prestamo = Prestamo(monto=1000, plazo=12, tasa_anual=12, frecuencia_pago='mensual')
        cuota = prestamo.calcular_cuota()
        self.assertAlmostEqual(cuota, 88.85, places=2)

    def test_calcular_cuota_semanal(self):
        prestamo = Prestamo(monto=1000, plazo=12, tasa_anual=12, frecuencia_pago='semanal')
        cuota = prestamo.calcular_cuota()
        self.assertAlmostEqual(cuota, 20.43, places=2)
