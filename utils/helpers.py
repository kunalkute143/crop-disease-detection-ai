# utils/helpers.py
import os
import uuid
import base64
from datetime import datetime
from PIL import Image
import io

def format_date(date, format='%d %b %Y, %I:%M %p'):
    """Format date for display"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return date.strftime(format)

def generate_unique_filename(prefix='', extension='jpg'):
    """Generate unique filename using UUID"""
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if prefix:
        filename = f"{prefix}_{timestamp}_{unique_id}.{extension}"
    else:
        filename = f"{timestamp}_{unique_id}.{extension}"
    
    return filename

def save_base64_image(base64_string, upload_folder, filename=None):
    """Save base64 encoded image to file"""
    try:
        # Remove header if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Create image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Generate filename if not provided
        if not filename:
            filename = generate_unique_filename('image', 'jpg')
        
        # Ensure filename is safe
        filename = secure_filename(filename)
        
        # Full path
        filepath = os.path.join(upload_folder, filename)
        
        # Save image
        image.save(filepath, 'JPEG', quality=85)
        
        return filename, filepath
        
    except Exception as e:
        print(f"Error saving base64 image: {e}")
        return None, None

def get_file_size(filepath):
    """Get file size in human readable format"""
    size_bytes = os.path.getsize(filepath)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"

def truncate_string(text, max_length=100, suffix='...'):
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def calculate_confidence_color(confidence):
    """Return color based on confidence level"""
    if confidence >= 0.8:
        return 'text-green-600'
    elif confidence >= 0.6:
        return 'text-yellow-600'
    else:
        return 'text-red-600'

def get_weather_advice(weather_data):
    """Generate farming advice based on weather"""
    advice = []
    
    if weather_data.get('rain'):
        advice.append("🌧️ Rain expected - Hold off on irrigation")
    
    if weather_data.get('temperature', 0) > 35:
        advice.append("🔥 High temperature - Ensure adequate irrigation")
    
    if weather_data.get('humidity', 0) > 80:
        advice.append("💧 High humidity - Monitor for fungal diseases")
    
    return advice if advice else ["✓ Weather conditions are favorable for farming"]

# Import for secure_filename
from werkzeug.utils import secure_filename