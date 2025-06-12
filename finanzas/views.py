from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone

from .models import Prestamo, Pago, IncrementoPrestamo, GestorSaldo
from .forms import PrestamoForm, PagoForm, IncrementoPrestamoForm


def inicio(request):
    GestorSaldo.actualizar_saldos()
    prestamos_recientes = Prestamo.objects.all().order_by('-fecha_inicio')[:5]
    return render(request, 'finanzas/inicio.html', {
        'prestamos_recientes': prestamos_recientes
    })


def lista_prestamos(request):
    GestorSaldo.actualizar_saldos()
    prestamos = Prestamo.objects.all().order_by('-fecha_inicio')
    return render(request, 'finanzas/lista_prestamos.html', {
        'prestamos': prestamos
    })


def calcular_pago(request):
    if request.method == 'POST':
        monto = float(request.POST['monto'])
        plazo = int(request.POST['plazo'])
        tasa_anual = float(request.POST['tasa_anual'])
        frecuencia_pago = request.POST['frecuencia_pago']

        # Guardamos los valores en sesión para usarlos en nuevo_prestamo
        request.session['monto'] = monto
        request.session['plazo'] = plazo
        request.session['tasa_anual'] = tasa_anual
        request.session['frecuencia_pago'] = frecuencia_pago

        return redirect('finanzas:nuevo_prestamo')
    return render(request, 'finanzas/calculadora.html')


def nuevo_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Préstamo registrado correctamente.")
            return redirect('finanzas:lista_prestamos')
    else:
        # Recuperar datos precalculados desde la sesión
        monto = request.session.get('monto')
        plazo = request.session.get('plazo')
        tasa_anual = request.session.get('tasa_anual')
        frecuencia_pago = request.session.get('frecuencia_pago')

        # Si falta algún dato, redirigir de vuelta a la calculadora
        if None in (monto, plazo, tasa_anual, frecuencia_pago):
            messages.warning(request, "⚠️ Primero realiza el cálculo del préstamo.")
            return redirect('finanzas:calcular_pago')

        form = PrestamoForm(initial={
            'monto': monto,
            'plazo': plazo,
            'tasa_anual': tasa_anual,
            'frecuencia_pago': frecuencia_pago,
        })

    return render(request, 'finanzas/form_prestamo.html', {'form': form})


def detalle_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    pagos = prestamo.pagos.all().order_by('-fecha_pago')
    incrementos = prestamo.incrementos.all().order_by('-fecha')
    return render(request, 'finanzas/detalle_prestamo.html', {
        'prestamo': prestamo,
        'pagos': pagos,
        'incrementos': incrementos
    })


def registrar_pago(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.prestamo = prestamo
            pago.save()
            messages.success(request, "✅ Pago registrado.")
            return redirect('finanzas:detalle_prestamo', prestamo_id=prestamo.id)
    else:
        form = PagoForm()
    return render(request, 'finanzas/form_pago.html', {
        'form': form,
        'prestamo': prestamo
    })


def incrementar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    if request.method == 'POST':
        form = IncrementoPrestamoForm(request.POST)
        if form.is_valid():
            incremento = form.save(commit=False)
            incremento.prestamo = prestamo
            incremento.save()
            messages.success(request, '✅ Incremento registrado.')
            return redirect('finanzas:detalle_prestamo', prestamo_id=prestamo.id)
    else:
        form = IncrementoPrestamoForm()
    return render(request, 'finanzas/form_incremento.html', {
        'form': form,
        'prestamo': prestamo
    })


def actualizar_saldos_view(request):
    GestorSaldo.actualizar_saldos()
    return HttpResponse("✅ Saldos actualizados correctamente.")
