from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('prestamo/nuevo/', views.nuevo_prestamo, name='nuevo_prestamo'),
    path('prestamo/<int:prestamo_id>/', views.detalle_prestamo, name='detalle_prestamo'),
    path('prestamo/<int:prestamo_id>/pago/', views.registrar_pago, name='registrar_pago'),
    path('prestamo/<int:prestamo_id>/incremento/', views.incrementar_prestamo, name='incrementar_prestamo'),
    path('calcular-pago/', views.calcular_pago, name='calcular_pago'),
    path('prestamos/', views.lista_prestamos, name='lista_prestamos'),
]
