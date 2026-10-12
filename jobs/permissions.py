from django.contrib.auth.decorators import user_passes_test


def can_manage_recruiter(user):
    return user.is_authenticated and (
        user.is_staff or user.has_perm('jobs.manage_recruiter_dashboard')
    )


recruiter_required = user_passes_test(
    can_manage_recruiter,
    login_url='recruiter:login',
    redirect_field_name='next',
)
