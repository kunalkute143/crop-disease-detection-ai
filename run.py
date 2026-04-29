import os
from app import app


def initialize_services():
    """Initialize ML model and chatbot services"""

    from services.ml_service import init_detector
    from services.chatbot_service import init_chatbot

    # Load ML model
    model_path = app.config.get("MODEL_PATH")
    class_indices_path = app.config.get("CLASS_INDICES_PATH")

    if model_path and os.path.exists(model_path):
        init_detector(model_path, class_indices_path)
        print("✅ ML Model loaded successfully")
    else:
        print(f"⚠️ Warning: Model not found at {model_path}")

    # Initialize chatbot with Gemini API
    gemini_api_key = app.config.get("GEMINI_API_KEY")
    use_gemini = bool(gemini_api_key)
    
    init_chatbot(use_gemini, gemini_api_key)
    
    if use_gemini:
        print("✅ Gemini AI Chatbot initialized")
    else:
        print("⚠️ Gemini API key not found, using fallback mode")


if __name__ == "__main__":

    # Ensure upload directory exists
    upload_folder = app.config.get("UPLOAD_FOLDER", "static/uploads")
    os.makedirs(upload_folder, exist_ok=True)
    
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)

    # Initialize services
    initialize_services()

    print("=" * 50)
    print("🚀 Smart Farming Assistant is running!")
    print("📱 Open: http://localhost:5000")
    print("=" * 50)

    # Run Flask app
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )