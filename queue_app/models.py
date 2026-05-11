from django.db import models
from django.utils import timezone


class QueueEntry(models.Model):
    STATUS_WAITING  = 'waiting'
    STATUS_CALLED   = 'called'
    STATUS_ATTENDED = 'attended'

    STATUS_CHOICES = [
        (STATUS_WAITING,  'Esperando'),
        (STATUS_CALLED,   'Llamado'),
        (STATUS_ATTENDED, 'Atendido'),
    ]

    name        = models.CharField(max_length=100, verbose_name='Nombre')
    phone       = models.CharField(max_length=20, verbose_name='Teléfono')
    turn_number = models.PositiveIntegerField(verbose_name='Turno')
    status      = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
        verbose_name='Estado',
    )
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='Registrado')
    called_at   = models.DateTimeField(null=True, blank=True, verbose_name='Llamado a las')
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name='Atendido a las')

    class Meta:
        ordering = ['turn_number']
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'

    def __str__(self):
        return f"Turno {self.turn_number} — {self.name} [{self.get_status_display()}]"

    def people_ahead(self):
        today = timezone.localdate()
        return QueueEntry.objects.filter(
            status=self.STATUS_WAITING,
            turn_number__lt=self.turn_number,
            created_at__date=today,
        ).count()
