# finanzas/management/commands/actualizar_saldos.py

from django.core.management.base import BaseCommand
from finanzas.models import GestorSaldo

class Command(BaseCommand):
    help = 'Actualiza los saldos de todos los préstamos según su frecuencia y pagos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔄 Iniciando actualización de saldos...'))
        GestorSaldo.actualizar_saldos()
        self.stdout.write(self.style.SUCCESS('✅ Saldos actualizados correctamente.'))
