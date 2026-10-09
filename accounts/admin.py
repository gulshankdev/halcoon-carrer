from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CandidateProfile


class CandidateProfileInline(admin.StackedInline):
    model = CandidateProfile
    can_delete = False
    verbose_name_plural = 'Candidate Profile Details'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (CandidateProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone', 'date_joined')

    def get_phone(self, obj):
        return obj.candidate_profile.phone if hasattr(obj, 'candidate_profile') else '-'
    get_phone.short_description = 'Phone'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'location', 'has_resume', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'location', 'skills')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def has_resume(self, obj):
        return bool(obj.resume)
    has_resume.boolean = True
    has_resume.short_description = 'Resume Uploaded'
