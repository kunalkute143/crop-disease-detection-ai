# utils/validators.py
import re
import os
from werkzeug.utils import secure_filename

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return False, "Please enter a valid email address"
    
    return True, "Email is valid"

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True, "Phone is optional"  # Phone is optional
    
    # Remove spaces, hyphens, etc
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's all digits and length between 10-15
    if not cleaned.isdigit():
        return False, "Phone number should contain only digits"
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Phone number should be between 10 and 15 digits"
    
    return True, "Phone number is valid"

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    return True, "Password is strong enough"

def validate_username(username):
    """Validate username"""
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    
    # Check for allowed characters
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Username is valid"

def validate_image_file(filename, allowed_extensions=None):
    """Validate image file extension"""
    if not filename:
        return False, "No file selected"
    
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    if '.' not in filename:
        return False, "Invalid file name"
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, "File type is valid"

def validate_file_size(file, max_size_mb=16):
    """Validate file size"""
    if not file:
        return False, "No file provided"
    
    # Check if file object has content_length attribute
    if hasattr(file, 'content_length') and file.content_length:
        size_mb = file.content_length / (1024 * 1024)
    else:
        # Try to get size from stream
        file.seek(0, os.SEEK_END)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)
    
    if size_mb > max_size_mb:
        return False, f"File size too large. Maximum allowed: {max_size_mb}MB"
    
    return True, "File size is acceptable"

def validate_crop_data(data):
    """Validate crop data"""
    required_fields = ['crop_name', 'planting_date']
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")
    
    return errors if errors else None

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove any script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()