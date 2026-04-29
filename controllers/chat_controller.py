# controllers/chat_controller.py
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from services.chatbot_service import get_chatbot
from services.voice_service import VoiceService
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)
voice_service = VoiceService()


@chat_bp.route('/assistant')
@login_required
def assistant():
    """Chat assistant page"""
    return render_template('chat/assistant.html')


@chat_bp.route('/api/message', methods=['POST'])
@login_required
def send_message():
    """Send message to chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        language = session.get('language', 'en')
        
        if not message:
            return jsonify({
                'status': 'error',
                'response': 'Please enter a message'
            }), 400
        
        # Get chatbot instance
        chatbot = get_chatbot()
        if not chatbot:
            return jsonify({
                'status': 'error',
                'response': 'Chatbot not initialized'
            }), 500
        
        # Get response from Gemini or rule-based
        response = chatbot.get_response(message, language)
        
        # Store conversation in session
        if 'conversation' not in session:
            session['conversation'] = []
        
        session['conversation'].append({
            'user': message,
            'bot': response,
            'timestamp': datetime.now().strftime('%H:%M:%S')  # ✅ UTC ऐवजी local time
        })
        
        # Keep only last 10 messages
        if len(session['conversation']) > 10:
            session['conversation'] = session['conversation'][-10:]
        
        return jsonify({
            'status': 'success',
            'response': response,
            'language': language,
            'gemini': getattr(chatbot, 'use_gemini', False)
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            'status': 'error',
            'response': 'An error occurred. Please try again.'
        }), 500


@chat_bp.route('/api/voice', methods=['POST'])
@login_required
def voice_message():
    """Handle voice input and output"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        language = session.get('language', 'en')
        action = data.get('action', 'process')
        
        if action == 'recognize':
            return jsonify({
                'status': 'success',
                'text': message,
                'message': 'Voice recognized'
            })
        
        elif action == 'speak':
            text = data.get('text', '')
            audio_data = voice_service.text_to_speech(text, language)
            
            return jsonify({
                'status': 'success',
                'audio': audio_data,
                'message': 'Speech generated'
            })
        
        else:  # process - both recognize and respond
            if not message:
                return jsonify({
                    'status': 'error',
                    'response': 'No voice input detected'
                }), 400
            
            chatbot = get_chatbot()
            if not chatbot:
                return jsonify({
                    'status': 'error',
                    'response': 'Chatbot not initialized'
                }), 500
            
            response = chatbot.get_response(message, language)
            audio_data = voice_service.text_to_speech(response, language)
            
            return jsonify({
                'status': 'success',
                'text': message,
                'response': response,
                'audio': audio_data,
                'language': language
            })
            
    except Exception as e:
        print(f"Voice error: {str(e)}")
        return jsonify({
            'status': 'error',
            'response': 'Voice processing failed'
        }), 500


@chat_bp.route('/api/clear', methods=['POST'])
@login_required
def clear_conversation():
    """Clear chat conversation"""
    session.pop('conversation', None)
    return jsonify({
        'status': 'success',
        'message': 'Conversation cleared'
    })


@chat_bp.route('/api/history')
@login_required
def get_history():
    """Get conversation history"""
    conversation = session.get('conversation', [])
    return jsonify({
        'status': 'success',
        'conversation': conversation
    })


@chat_bp.route('/api/suggestions')
@login_required
def get_suggestions():
    """Get suggested questions based on language"""
    language = session.get('language', 'en')
    
    # ✅ Rice and Mango specific suggestions
    suggestions_en = [
        "🌾 How to identify rice blast disease?",
        "🌾 Brown spot treatment for rice?",
        "🦠 Bacterial blight in rice symptoms?",
        "🥭 How to control mango anthracnose?",
        "🥭 Powdery mildew treatment for mango?",
        "💧 Best irrigation method for rice?",
        "🌱 Organic fertilizer for rice crop?",
        "🌿 Neem oil uses in farming"
    ]
    
    suggestions_mr = [
        "🌾 तांदळाचा ब्लास्ट रोग कसा ओळखावा?",
        "🌾 तांदळातील तपकिरी डागांवर उपचार?",
        "🦠 तांदळातील जिवाणूजन्य रोगाची लक्षणे?",
        "🥭 आंब्यातील करपा रोग कसा नियंत्रित करावा?",
        "🥭 आंब्यातील भुरी रोगावर उपचार?",
        "💧 तांदळासाठी सर्वोत्तम सिंचन पद्धत?",
        "🌱 तांदळासाठी सेंद्रिय खत?",
        "🌿 शेतीत निंबोळी तेलाचे उपयोग"
    ]
    
    suggestions = suggestions_mr if language == 'mr' else suggestions_en
    
    return jsonify({
        'status': 'success',
        'suggestions': suggestions,
        'language': language
    })