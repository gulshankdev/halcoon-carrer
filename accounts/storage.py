from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class ProtectedResumeStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.PROTECTED_MEDIA_ROOT)


def get_resume_path(file_field):
    if not file_field:
        return None

    stored_path = Path(file_field.path)
    if stored_path.is_file():
        return stored_path

    media_root = Path(settings.MEDIA_ROOT).resolve()
    legacy_path = (media_root / Path(*PurePosixPath(file_field.name).parts)).resolve()
    if legacy_path.is_relative_to(media_root) and legacy_path.is_file():
        return legacy_path
    return None
