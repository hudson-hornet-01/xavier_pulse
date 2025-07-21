from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "venue", "is_paid", "created_by")
    search_fields = ("name", "venue", "created_by__username")
    list_filter = ("is_paid", "date")
