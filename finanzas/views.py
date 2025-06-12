from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Prestamo, Pago, IncrementoPrestamo
from .forms import PrestamoForm, PagoForm, IncrementoPrestamoForm
from django.http import JsonResponse
from decimal import Decimal

from django.shortcuts import render

# finanzas/views.py
from django.shortcuts import render
from .models import Prestamo

# finanzas/views.py
from django.shortcuts import render
from .models import Prestamo

def inicio(request):
    # Cambiamos fecha_creacion por fecha_inicio
    prestamos_recientes = Prestamo.objects.all().order_by('-fecha_inicio')[:5]
    return render(request, 'finanzas/inicio.html', {
        'prestamos_recientes': prestamos_recientes
    })




def calcular_pago(request):
    if request.method == 'POST':
        monto = Decimal(request.POST.get('monto', 0))
        plazo = int(request.POST.get('plazo', 12))
        tasa_anual = Decimal(request.POST.get('tasa_anual', 0))
        frecuencia = request.POST.get('frecuencia_pago', 'mensual')

        prestamo_temp = Prestamo(
            monto=monto,
            plazo=plazo,
            tasa_anual=tasa_anual,
            frecuencia_pago=frecuencia
        )

        cuota = prestamo_temp.calcular_cuota()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'cuota': float(cuota),
                'total_a_pagar': float(cuota * (plazo * (12 if frecuencia == 'mensual' else 52))),
            })
        else:
            # Para solicitudes normales POST, renderizar la página con los resultados
            return render(request, 'finanzas/calcular_pago.html', {
                'cuota': cuota,
                'total_a_pagar': cuota * (plazo * (12 if frecuencia == 'mensual' else 52)),
                'monto': monto,
                'plazo': plazo,
                'tasa_anual': tasa_anual,
                'frecuencia': frecuencia
            })

    # GET request - mostrar el formulario vacío
    return render(request, 'finanzas/calcular_pago.html')


def lista_prestamos(request):
    prestamos = Prestamo.objects.all().order_by('-fecha_inicio')
    return render(request, 'finanzas/lista_prestamos.html', {
        'prestamos': prestamos
    })


def detalle_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    pagos = prestamo.pagos.all().order_by('-fecha_pago')
    incrementos = prestamo.incrementos.all().order_by('-fecha')
    return render(request, 'finanzas/detalle_prestamo.html', {
        'prestamo': prestamo,
        'pagos': pagos,
        'incrementos': incrementos
    })


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Prestamo
from .forms import PrestamoForm


def nuevo_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            try:
                prestamo = form.save()
                messages.success(request, 'Préstamo creado exitosamente.')
                return redirect('detalle_prestamo', pk=prestamo.pk)
            except Exception as e:
                messages.error(request, f'Error al crear el préstamo: {str(e)}')
                print(f"Error al crear préstamo: {str(e)}")  # Para depuración
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
            print(f"Errores del formulario: {form.errors}")  # Para depuración
    else:
        form = PrestamoForm()

    return render(request, 'finanzas/nuevo_prestamo.html', {
        'form': form,
        'titulo': 'Nuevo Préstamo'
    })


def detalle_prestamo(request, pk):
    try:
        prestamo = Prestamo.objects.get(pk=pk)
        return render(request, 'finanzas/detalle_prestamo.html', {
            'prestamo': prestamo,
            'titulo': f'Préstamo de {prestamo.nombre_cliente}'
        })
    except Prestamo.DoesNotExist:
        messages.error(request, 'El préstamo no existe.')
        return redirect('lista_prestamos')


from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Prestamo, Pago
from .forms import PrestamoForm, PagoForm


def registrar_pago(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.prestamo = prestamo
            pago.save()
            return redirect('finanzas:detalle_prestamo', prestamo_id=prestamo_id)
    else:
        form = PagoForm()

    return render(request, 'finanzas/form_pago.html', {
        'form': form,
        'prestamo': prestamo
    })


def detalle_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    pagos = prestamo.pagos.all().order_by('-fecha_pago')

    return render(request, 'finanzas/detalle_prestamo.html', {
        'prestamo': prestamo,
        'pagos': pagos
    })


def incrementar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    if request.method == 'POST':
        form = IncrementoPrestamoForm(request.POST)
        if form.is_valid():
            incremento = form.save(commit=False)
            incremento.prestamo = prestamo
            incremento.save()
            messages.success(request, 'Incremento registrado exitosamente.')
            return redirect('finanzas:detalle_prestamo', prestamo_id=prestamo.id)
    else:
        form = IncrementoPrestamoForm()
    return render(request, 'finanzas/form_incremento.html', {
        'form': form,
        'prestamo': prestamo
    })

def lista_prestamos(request):
    prestamos = Prestamo.objects.all()
    return render(request, 'finanzas/lista_prestamos.html', {
        'prestamos': prestamos
    })

