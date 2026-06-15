"""
File upload service — stores files in S3-compatible storage (MinIO in dev, AWS S3 in prod).
Validates file type and size before upload.
"""
from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

import structlog
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

log = structlog.get_logger(__name__)

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_ALLOWED_DOC_TYPES = {"application/pdf", "application/msword"}
_ALLOWED_MEDIA_TYPES = _ALLOWED_IMAGE_TYPES | {"video/mp4", "video/quicktime"}

_S3_CLIENT = None


def _get_s3():
    global _S3_CLIENT
    if _S3_CLIENT is None:
        import boto3
        _S3_CLIENT = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )
    return _S3_CLIENT


def _validate_file(file: UploadFile, allowed_types: set[str]) -> str:
    content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{content_type}' is not allowed",
        )
    return content_type


async def _upload(file: UploadFile, key: str, content_type: str) -> str:
    contents = await file.read()
    if len(contents) > settings.max_file_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB",
        )
    try:
        s3 = _get_s3()
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=contents,
            ContentType=content_type,
        )
        base = settings.S3_ENDPOINT_URL or f"https://s3.amazonaws.com"
        return f"{base}/{settings.S3_BUCKET_NAME}/{key}"
    except Exception as e:
        log.exception("S3 upload failed", key=key)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")


async def upload_avatar(file: UploadFile, user_id: str) -> str:
    ct = _validate_file(file, _ALLOWED_IMAGE_TYPES)
    ext = Path(file.filename or "avatar").suffix or ".jpg"
    key = f"avatars/{user_id}/{uuid.uuid4()}{ext}"
    return await _upload(file, key, ct)


async def upload_report_media(file: UploadFile, report_id: str) -> tuple[str, str]:
    """Returns (url, media_type_label)."""
    ct = _validate_file(file, _ALLOWED_MEDIA_TYPES)
    ext = Path(file.filename or "media").suffix or ".jpg"
    key = f"reports/{report_id}/{uuid.uuid4()}{ext}"
    url = await _upload(file, key, ct)
    label = "image" if ct.startswith("image") else "video"
    return url, label
