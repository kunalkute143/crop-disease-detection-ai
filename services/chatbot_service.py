# services/chatbot_service.py
import re
import random
import google.generativeai as genai

class FarmingChatbot:
    def __init__(self, use_gemini=False, gemini_api_key=None):
        self.use_gemini = use_gemini
        self.gemini_api_key = gemini_api_key
        
        # Initialize Gemini if available
        if use_gemini and gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                # ✅ नवीन model - gemini-1.5-flash (gemini-pro deprecated आहे)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Gemini API initialized (gemini-2.5-flash)")
            except Exception as e:
                print(f"⚠️ Gemini API failed: {e}")
                self.use_gemini = False
        
        # Simple rule-based responses
        self.responses = {
            'greetings': {
                'patterns': ['hello', 'hi', 'hey', 'namaste', 'नमस्ते', 'नमस्कार', 'हॅलो'],
                'en': '🌾 Hello! I am your farming assistant. Ask me about rice, mango, diseases, fertilizers, or upload a photo for detection!',
                'mr': '🌾 नमस्ते! मी तुमचा शेती सहाय्यक आहे. तांदूळ, आंबा, रोग, खते यांबद्दल विचारा किंवा फोटो अपलोड करा!'
            },
            'rice': {
                'patterns': ['rice', 'तांदूळ', 'भात', 'तांदळाचे', 'तांदळासाठी'],
                'en': '🌾 **Rice Farming Tips:**\n\n• **Diseases:** Blast, Brown Spot, Bacterial Blight\n• **Fertilizers:** NPK 20:20:20 (2g/L), Vermicompost (5kg/plant)\n• **Water:** Drip irrigation, alternate wetting-drying\n• **Detection:** Upload leaf photo for AI diagnosis!',
                'mr': '🌾 **तांदूळ शेती टिप्स:**\n\n• **रोग:** ब्लास्ट, तपकिरी डाग, जिवाणूजन्य रोग\n• **खते:** NPK 20:20:20 (2g/L), वर्मीकंपोस्ट (5kg/झाड)\n• **पाणी:** ठिबक सिंचन, आलटून-पालटून ओले-कोरडे\n• **ओळख:** रोग ओळखीसाठी पानाचा फोटो अपलोड करा!'
            },
            'rice_fertilizer': {
                'patterns': ['rice fertilizer', 'तांदूळ खत', 'तांदळाचे खत', 'भातासाठी खत'],
                'en': '🌾 **Best Fertilizers for Rice:**\n\n**Organic:**\n• Vermicompost: 5kg/plant\n• Neem Cake: 500g/plant\n• Compost: 2kg/plant\n\n**Chemical:**\n• NPK 20:20:20: 2g/L (foliar)\n• Urea: 50kg/acre (split doses)\n• DAP: 40kg/acre (basal)\n\n**Bio-Fertilizer:**\n• Trichoderma: 2g/L\n• Pseudomonas: 1g/L',
                'mr': '🌾 **तांदळासाठी सर्वोत्तम खते:**\n\n**सेंद्रिय:**\n• वर्मीकंपोस्ट: 5kg/झाड\n• निंबोळी खत: 500g/झाड\n• कंपोस्ट: 2kg/झाड\n\n**रासायनिक:**\n• NPK 20:20:20: 2g/L (पानांवर)\n• युरिया: 50kg/एकर\n• DAP: 40kg/एकर\n\n**जैविक खत:**\n• ट्रायकोडर्मा: 2g/L\n• स्यूडोमोनास: 1g/L'
            },
            'mango': {
                'patterns': ['mango', 'आंबा', 'आंब्याचे', 'आंब्यासाठी'],
                'en': '🥭 **Mango Farming Tips:**\n\n• **Diseases:** Anthracnose, Powdery Mildew\n• **Treatment:** Copper fungicide before flowering\n• **Fertilizer:** NPK 15:15:15 (3g/L), Vermicompost\n• **Pruning:** Regular pruning for air circulation',
                'mr': '🥭 **आंबा शेती टिप्स:**\n\n• **रोग:** करपा, भुरी\n• **उपचार:** फुलोऱ्यापूर्वी तांबे बुरशीनाशक\n• **खत:** NPK 15:15:15 (3g/L), वर्मीकंपोस्ट\n• **छाटणी:** हवा खेळती ठेवण्यासाठी नियमित छाटणी'
            },
            'disease': {
                'patterns': ['disease', 'रोग', 'आजार', 'sick', 'ब्लास्ट', 'डाग', 'लक्षणे'],
                'en': '🔍 **Disease Detection:**\n\nUpload a clear photo of the affected leaf using the "Upload Crop" feature. Our AI model will:\n✅ Identify the disease\n✅ Suggest organic & chemical solutions\n✅ Provide 8-10 day treatment plan\n\n**Tip:** Take photo in natural light for best results!',
                'mr': '🔍 **रोग ओळख:**\n\nरोगग्रस्त पानाचा स्पष्ट फोटो "पीक अपलोड करा" वैशिष्ट्य वापरून अपलोड करा. आमचे एआय मॉडेल:\n✅ रोग ओळखेल\n✅ सेंद्रिय व रासायनिक उपाय सुचवेल\n✅ ८-१० दिवसांची उपचार योजना देईल\n\n**टीप:** चांगल्या प्रकाशात फोटो काढा!'
            },
            'organic': {
                'patterns': ['organic', 'natural', 'सेंद्रिय', 'जैविक', 'नैसर्गिक'],
                'en': '🌱 **Organic Farming Solutions:**\n\n• **Pest Control:** Neem oil spray (5ml/L water)\n• **Disease Control:** Compost tea, Trichoderma\n• **Fertilizer:** Vermicompost, Cow dung manure\n• **Soil Health:** Crop rotation, Green manure\n• **Weed Control:** Mulching, Manual weeding',
                'mr': '🌱 **सेंद्रिय शेती उपाय:**\n\n• **कीड नियंत्रण:** निंबोळी तेल फवारणी (5ml/L पाणी)\n• **रोग नियंत्रण:** कंपोस्ट टी, ट्रायकोडर्मा\n• **खत:** वर्मीकंपोस्ट, शेणखत\n• **जमीन सुपीकता:** पीक फेरपालट, हिरवळीचे खत\n• **तण नियंत्रण:** आच्छादन, हाताने तण काढणे'
            },
            'fertilizer': {
                'patterns': ['fertilizer', 'खत', 'manure', 'compost', 'युरिया', 'खते'],
                'en': '🌿 **Fertilizer Guide:**\n\n**Organic:**\n• Vermicompost: 5kg/plant\n• Neem Cake: 500g/plant\n• Compost: 2kg/plant\n\n**Chemical:**\n• NPK 20:20:20: 2g/L (foliar)\n• Urea: 50kg/acre (split doses)\n• DAP: 40kg/acre\n\n**Bio-Fertilizer:**\n• Trichoderma: 2g/L soil\n• Pseudomonas: 1g/L spray',
                'mr': '🌿 **खत मार्गदर्शक:**\n\n**सेंद्रिय:**\n• वर्मीकंपोस्ट: 5kg/झाड\n• निंबोळी खत: 500g/झाड\n• कंपोस्ट: 2kg/झाड\n\n**रासायनिक:**\n• NPK 20:20:20: 2g/L (पानांवर)\n• युरिया: 50kg/एकर\n• DAP: 40kg/एकर\n\n**जैविक खत:**\n• ट्रायकोडर्मा: 2g/L मातीत\n• स्यूडोमोनास: 1g/L फवारणी'
            },
            'water': {
                'patterns': ['water', 'पाणी', 'irrigation', 'सिंचन', 'ठिबक', 'सिंचनासाठी'],
                'en': '💧 **Water Management Tips:**\n\n• **Best Time:** Early morning or late evening\n• **Method:** Drip irrigation saves 40% water\n• **For Rice:** Alternate wetting and drying (AWD)\n• **Mulching:** Retains soil moisture\n• **Avoid:** Over-irrigation causes root rot',
                'mr': '💧 **पाणी व्यवस्थापन टिप्स:**\n\n• **योग्य वेळ:** सकाळी लवकर किंवा संध्याकाळी\n• **पद्धत:** ठिबक सिंचनाने 40% पाणी वाचते\n• **तांदळासाठी:** आलटून-पालटून ओले-कोरडे\n• **आच्छादन:** मातीतील ओलावा टिकवतो\n• **टाळा:** जास्त पाण्याने मुळे कुजतात'
            },
            'help': {
                'patterns': ['help', 'मदत', 'कसे', 'काय', 'सांगा'],
                'en': '🤖 **I can help you with:**\n\n📸 **Crop Disease Detection** - Upload photo\n🌾 **Rice Farming** - Diseases, fertilizers, water\n🥭 **Mango Farming** - Diseases, treatment\n🌱 **Organic Solutions** - Natural pest control\n💧 **Water Management** - Irrigation tips\n🌿 **Fertilizers** - Organic & chemical\n\nJust ask or upload a photo!',
                'mr': '🤖 **मी यामध्ये मदत करू शकतो:**\n\n📸 **पीक रोग ओळख** - फोटो अपलोड करा\n🌾 **तांदूळ शेती** - रोग, खते, पाणी\n🥭 **आंबा शेती** - रोग, उपचार\n🌱 **सेंद्रिय उपाय** - नैसर्गिक कीड नियंत्रण\n💧 **पाणी व्यवस्थापन** - सिंचन टिप्स\n🌿 **खते** - सेंद्रिय व रासायनिक\n\nफक्त विचारा किंवा फोटो अपलोड करा!'
            }
        }
        
        self.default = {
            'en': '🌾 I am your farming assistant. You can ask me about:\n\n• Rice and Mango farming\n• Crop diseases and treatment\n• Organic and chemical fertilizers\n• Water management\n\nOr upload a photo for AI disease detection!',
            'mr': '🌾 मी तुमचा शेती सहाय्यक आहे. तुम्ही विचारू शकता:\n\n• तांदूळ आणि आंबा शेती\n• पीक रोग आणि उपचार\n• सेंद्रिय व रासायनिक खते\n• पाणी व्यवस्थापन\n\nकिंवा रोग ओळखीसाठी फोटो अपलोड करा!'
        }
    
    def get_response(self, message, language='en'):
        """Get response from Gemini or rule-based"""
        
        # Try Gemini first
        if self.use_gemini and hasattr(self, 'model'):
            try:
                prompt = f"""You are a helpful farming assistant. Answer in {'Marathi' if language == 'mr' else 'English'}.
Question: {message}

Give practical, specific advice. Keep it concise and useful for farmers."""
                
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini error: {e}")
                # Continue to rule-based
        else:
            print("⚠️ Gemini not available, using rule-based")
        
        # Rule-based response
        return self.get_rule_response(message, language)
    
    def get_rule_response(self, message, language='en'):
        """Simple rule-based response"""
        msg = message.lower().strip()
        
        # Specific patterns for rice fertilizer
        if ('rice' in msg or 'तांदूळ' in msg) and ('fertilizer' in msg or 'खत' in msg):
            return self.responses['rice_fertilizer'][language]
        
        # Find matching pattern
        for key, val in self.responses.items():
            for pattern in val['patterns']:
                if pattern.lower() in msg:
                    return val[language]
        
        # Default response
        return self.default.get(language, self.default['en'])


# Global instance
_chatbot = None

def init_chatbot(use_gemini=False, gemini_api_key=None):
    global _chatbot
    _chatbot = FarmingChatbot(use_gemini, gemini_api_key)
    return _chatbot

def get_chatbot():
    return _chatbot