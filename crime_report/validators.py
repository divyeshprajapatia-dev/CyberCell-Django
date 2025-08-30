import os
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.defaultfilters import filesizeformat

def validate_file_extension(value):
    """Validate file extension for uploaded files."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [f'.{ext}' for ext in settings.MEDIA_FILE_EXTENSIONS]
    
    if not ext in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension. Allowed extensions are: {", ".join(settings.MEDIA_FILE_EXTENSIONS)}'
        )

def validate_file_size(value):
    """Validate file size for uploaded files."""
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'Please keep filesize under {filesizeformat(settings.MAX_UPLOAD_SIZE)}. Current filesize {filesizeformat(value.size)}'
        )

def validate_file_content(value):
    """Validate file content type and scan for potential malware."""
    # Check MIME type
    content_type = value.content_type.lower()
    allowed_types = [
        'image/jpeg',
        'image/png',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if content_type not in allowed_types:
        raise ValidationError('Unsupported file type.')
    
    # Basic file header check for common file types
    try:
        header = value.read(10)
        value.seek(0)  # Reset file pointer
        
        # Check for common file signatures
        jpeg_signatures = [b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1']
        png_signature = b'\x89PNG\r\n\x1a\n'
        pdf_signature = b'%PDF-'
        
        if content_type.startswith('image/jpeg') and not any(header.startswith(sig) for sig in jpeg_signatures):
            raise ValidationError('Invalid JPEG file.')
        elif content_type == 'image/png' and not header.startswith(png_signature):
            raise ValidationError('Invalid PNG file.')
        elif content_type == 'application/pdf' and not header.startswith(pdf_signature):
            raise ValidationError('Invalid PDF file.')
            
    except Exception:
        raise ValidationError('Unable to verify file content.')