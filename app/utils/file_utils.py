"""Filesystem and storage utility helpers."""

import logging
import uuid
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


def generate_unique_filename(extension: str) -> str:
    """Generate a collision-resistant unique filename using UUID4."""
    ext = extension.lstrip(".")
    return f"{uuid.uuid4().hex}.{ext}"


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure that the given directory exists, creating parents if needed."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_delete_file(file_path: Union[str, Path]) -> bool:
    """Safely delete a file from the filesystem.
    
    Returns True if removed, False if file did not exist or deletion failed.
    Logs errors safely without leaking internal system details.
    """
    path = Path(file_path)
    try:
        if path.exists() and path.is_file():
            path.unlink()
            logger.info("Successfully deleted stored file: %s", path.name)
            return True
        logger.warning("File requested for deletion was not found: %s", path.name)
        return False
    except OSError as err:
        logger.error("Failed to delete file '%s': %s", path.name, str(err))
        return False
