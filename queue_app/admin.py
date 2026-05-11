from django.contrib import admin
from .models import QueueEntry


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    list_display    = ('turn_number', 'name', 'phone', 'status', 'created_at', 'called_at')
    list_filter     = ('status', 'created_at')
    search_fields   = ('name', 'phone')
    readonly_fields = ('turn_number', 'created_at', 'called_at', 'attended_at')
    ordering        = ('-created_at', 'turn_number')
