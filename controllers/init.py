# controllers/__init__.py
from .auth_controller import auth_bp
from .crop_controller import crop_bp
from .chat_controller import chat_bp
from .dashboard_controller import dashboard_bp

# Export all blueprints for easy import
__all__ = ['auth_bp', 'crop_bp', 'chat_controller', 'dashboard_bp']