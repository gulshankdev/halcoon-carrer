from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_resolved',)
    ordering = ('-created_at',)
