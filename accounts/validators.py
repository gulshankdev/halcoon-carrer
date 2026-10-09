import os
from django.core.exceptions import ValidationError

ALLOWED_RESUME_EXTENSIONS = ['.pdf', '.docx', '.doc']
MAX_RESUME_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_resume_file(value):
    """
    Validates that uploaded resume is in an allowed document format
    and does not exceed the maximum file size (5MB).
    """
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file format '{ext}'. Allowed formats are PDF, DOCX, and DOC."
        )

    if value.size > MAX_RESUME_FILE_SIZE:
        size_in_mb = value.size / (1024 * 1024)
        raise ValidationError(
            f"File size ({size_in_mb:.1f} MB) exceeds maximum allowed limit of 5 MB."
        )

