from django.contrib import admin
from .models import Category, Job


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('active',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'employer_name',
        'category',
        'location',
        'employment_type',
        'experience_requirements',
        'is_published',
        'is_featured',
        'created_at',
    )
    list_filter = (
        'is_published',
        'is_featured',
        'employment_type',
        'experience_requirements',
        'category',
        'created_at',
    )
    search_fields = (
        'title',
        'employer_name',
        'location',
        'description',
        'required_skills',
        'responsibilities',
    )
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'created_at'
    actions = ['publish_jobs', 'unpublish_jobs', 'feature_jobs']

    @admin.action(description="Publish selected vacancies")
    def publish_jobs(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} vacancies successfully published.")

    @admin.action(description="Unpublish/Archive selected vacancies")
    def unpublish_jobs(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} vacancies moved to draft/archive.")

    @admin.action(description="Mark selected vacancies as Featured")
    def feature_jobs(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} vacancies marked as featured on homepage.")
