import logging
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import sms
from .models import QueueEntry

logger = logging.getLogger('queue_app')


def _assign_turn_number():
    today = timezone.localdate()
    last = (
        QueueEntry.objects
        .filter(created_at__date=today)
        .select_for_update()
        .order_by('-turn_number')
        .first()
    )
    return (last.turn_number + 1) if last else 1


def _normalize_phone(phone):
    """Strip spaces and dashes; ensure leading + is preserved."""
    phone = re.sub(r'[\s\-]', '', phone.strip())
    return phone


def register(request):
    error = None
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        phone = _normalize_phone(request.POST.get('phone', ''))

        if not name:
            error = 'Por favor ingresa tu nombre.'
        elif not phone:
            error = 'Por favor ingresa tu número de teléfono.'
        else:
            with transaction.atomic():
                turn = _assign_turn_number()
                entry = QueueEntry.objects.create(
                    name=name,
                    phone=phone,
                    turn_number=turn,
                    status=QueueEntry.STATUS_WAITING,
                )
            return redirect('queue_app:confirmation', turn_number=entry.turn_number)

    return render(request, 'queue_app/register.html', {'error': error})


def confirmation(request, turn_number):
    today = timezone.localdate()
    entry = get_object_or_404(QueueEntry, turn_number=turn_number, created_at__date=today)
    return render(request, 'queue_app/confirmation.html', {
        'entry': entry,
        'ahead': entry.people_ahead(),
    })


def display(request):
    today = timezone.localdate()
    current = (
        QueueEntry.objects
        .filter(status=QueueEntry.STATUS_CALLED, created_at__date=today)
        .order_by('-called_at')
        .first()
    )
    return render(request, 'queue_app/display.html', {'current': current})


@login_required
def admin_panel(request):
    today = timezone.localdate()
    entries = QueueEntry.objects.filter(created_at__date=today)
    counts = {
        'waiting':  entries.filter(status=QueueEntry.STATUS_WAITING).count(),
        'called':   entries.filter(status=QueueEntry.STATUS_CALLED).count(),
        'attended': entries.filter(status=QueueEntry.STATUS_ATTENDED).count(),
    }
    return render(request, 'queue_app/admin_panel.html', {
        'entries': entries,
        'counts':  counts,
    })


@login_required
@require_POST
def call_next(request):
    today = timezone.localdate()
    entry = (
        QueueEntry.objects
        .filter(status=QueueEntry.STATUS_WAITING, created_at__date=today)
        .order_by('turn_number')
        .first()
    )
    if not entry:
        messages.warning(request, 'No hay más turnos en espera.')
        return redirect('queue_app:admin_panel')

    entry.status    = QueueEntry.STATUS_CALLED
    entry.called_at = timezone.now()
    entry.save()

    try:
        sms.send_called_notification(entry)
    except Exception as exc:
        logger.error("SMS failed for turn %s: %s", entry.turn_number, exc)
        messages.warning(request, f'Turno {entry.turn_number} llamado, pero el SMS no pudo enviarse.')
    else:
        messages.success(request, f'Turno {entry.turn_number} — {entry.name} llamado. SMS enviado.')

    return redirect('queue_app:admin_panel')


@login_required
@require_POST
def mark_attended(request, entry_id):
    entry = get_object_or_404(QueueEntry, pk=entry_id)
    entry.status      = QueueEntry.STATUS_ATTENDED
    entry.attended_at = timezone.now()
    entry.save()
    messages.success(request, f'Turno {entry.turn_number} marcado como atendido.')
    return redirect('queue_app:admin_panel')


@login_required
@require_POST
def reset_queue(request):
    today = timezone.localdate()
    count, _ = QueueEntry.objects.filter(created_at__date=today).delete()
    messages.success(request, f'Cola reiniciada. {count} turno(s) eliminado(s).')
    return redirect('queue_app:admin_panel')
