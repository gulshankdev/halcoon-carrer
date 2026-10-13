"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Ensure database tables and initial categories exist automatically on server startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    from jobs.models import Category
    if not Category.objects.exists():
        call_command('seed_sample_data')
except Exception as e:
    import logging
    logging.getLogger('django').warning(f"WSGI startup migration notice: {e}")

