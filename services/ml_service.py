# services/ml_service.py
import tensorflow as tf
import numpy as np
from PIL import Image, ImageStat, ImageFilter
import json
import os
import math

class CropDiseaseDetector:
    def __init__(self, model_path, class_indices_path):
        self.model = None
        self.class_indices = {}
        self.model_path = model_path
        self.class_indices_path = class_indices_path
        self.input_size = (224, 224)
        self.CONFIDENCE_THRESHOLD = 0.60
        self.load_model()
        self.load_class_indices()
    
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("✅ Model loaded successfully")
            else:
                print(f"⚠️ Model not found at {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def load_class_indices(self):
        try:
            if os.path.exists(self.class_indices_path):
                with open(self.class_indices_path, 'r') as f:
                    self.class_indices = json.load(f)
                self.class_indices = {v: k for k, v in self.class_indices.items()}
                print(f"✅ Loaded {len(self.class_indices)} classes")
        except Exception as e:
            print(f"❌ Error loading class indices: {e}")
    
    def is_crop_leaf(self, image):
        """
        Advanced validation to detect if image contains a crop leaf
        Using multiple image features
        """
        # Convert to RGB
        img = image.convert('RGB')
        w, h = img.size
        
        # 1. Get image as numpy array
        pixels = np.array(img)
        
        # 2. Analyze color distribution
        # Crop leaves typically have structured patterns, not uniform colors
        r_channel = pixels[:, :, 0].flatten()
        g_channel = pixels[:, :, 1].flatten()
        b_channel = pixels[:, :, 2].flatten()
        
        # Calculate color variance (leaves have variance, solid colors have low variance)
        r_var = np.var(r_channel)
        g_var = np.var(g_channel)
        b_var = np.var(b_channel)
        total_var = (r_var + g_var + b_var) / 3
        
        # If variance is too low, it might be a solid color image (not a real leaf)
        if total_var < 500:
            return False, "Image looks like a solid color block, not a crop leaf"
        
        # 3. Check texture using edge detection
        # Convert to grayscale
        gray = img.convert('L')
        # Apply edge detection filter
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_pixels = np.array(edges).flatten()
        edge_density = np.sum(edge_pixels > 30) / len(edge_pixels)
        
        # Real leaves have some edge density, solid colors have very low edge density
        if edge_density < 0.05:
            return False, "Image lacks natural texture - may not be a real crop leaf"
        
        # 4. Check if image has too uniform pattern (like screenshot, logo, etc.)
        # Divide image into 4 quadrants and check similarity
        h1, h2 = h // 2, h - h // 2
        w1, w2 = w // 2, w - w // 2
        
        # Get 4 quadrants
        quad1 = pixels[:h1, :w1].flatten()
        quad2 = pixels[:h1, w1:w].flatten()
        quad3 = pixels[h1:h, :w1].flatten()
        quad4 = pixels[h1:h, w1:w].flatten()
        
        # Calculate mean of each quadrant
        mean1 = np.mean(quad1)
        mean2 = np.mean(quad2)
        mean3 = np.mean(quad3)
        mean4 = np.mean(quad4)
        
        means = [mean1, mean2, mean3, mean4]
        mean_std = np.std(means)
        
        # If all quadrants are too similar, might be artificial image
        if mean_std < 10 and total_var < 1000:
            return False, "Image has uniform pattern - not a natural crop leaf"
        
        return True, "Valid crop leaf image"
    
    def is_valid_crop_image(self, image_path):
        """Validate if image is a real crop leaf"""
        try:
            img = Image.open(image_path)
            
            # Basic dimension check
            w, h = img.size
            if w < 50 or h < 50:
                return False, "Image too small (minimum 50x50 pixels)"
            if w > 4000 or h > 4000:
                return False, "Image too large (maximum 4000x4000 pixels)"
            
            # Aspect ratio check
            aspect_ratio = max(w, h) / min(w, h)
            if aspect_ratio > 4:
                return False, "Image aspect ratio too extreme"
            
            # Brightness check
            img_rgb = img.convert('RGB')
            stat = ImageStat.Stat(img_rgb)
            brightness = sum(stat.mean) / 3
            
            if brightness < 20:
                return False, "Image too dark. Please take photo in good lighting"
            if brightness > 240:
                return False, "Image too bright/overexposed"
            
            # Sharpness check
            std_dev = sum(stat.stddev) / 3
            if std_dev < 10:
                return False, "Image too blurry. Please take a clearer photo"
            
            # ✅ Advanced crop leaf detection
            is_leaf, reason = self.is_crop_leaf(img)
            if not is_leaf:
                return False, reason
            
            return True, "Valid crop leaf image"
            
        except Exception as e:
            return False, f"Error processing image: {str(e)}"
    
    def preprocess_image(self, image_path, target_size=(224, 224)):
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize(target_size)
            img_array = np.array(img)
            img_array = img_array.astype('float32') / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            return None
    
    def predict(self, image_path):
        """Make prediction with validation"""
        
        # Step 1: Basic image validation
        is_valid, reason = self.is_valid_crop_image(image_path)
        if not is_valid:
            return {
                'disease': 'Invalid',
                'confidence': 0,
                'is_valid': False,
                'message': reason,
                'class_index': -1
            }
        
        # Step 2: Make prediction
        if self.model is None:
            return {
                'disease': 'Model not loaded',
                'confidence': 0,
                'is_valid': False,
                'message': 'AI model not loaded. Please try again later.',
                'class_index': -1
            }
        
        processed_image = self.preprocess_image(image_path)
        if processed_image is None:
            return {
                'disease': 'Invalid',
                'confidence': 0,
                'is_valid': False,
                'message': 'Could not process image. Please try another image.',
                'class_index': -1
            }
        
        try:
            predictions = self.model.predict(processed_image, verbose=0)
            confidence = float(np.max(predictions[0]))
            predicted_class = np.argmax(predictions[0])
            disease_name = self.class_indices.get(predicted_class, 'Unknown')
            
            # Step 3: Check if confidence is high enough
            if confidence < self.CONFIDENCE_THRESHOLD:
                return {
                    'disease': 'Uncertain',
                    'confidence': confidence,
                    'is_valid': False,
                    'message': f'Low confidence ({confidence*100:.1f}%) in prediction. Please upload a clearer photo.',
                    'class_index': predicted_class
                }
            
            # Step 4: Valid prediction
            return {
                'disease': disease_name,
                'confidence': confidence,
                'is_valid': True,
                'message': 'Success',
                'class_index': predicted_class
            }
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return {
                'disease': 'Error',
                'confidence': 0,
                'is_valid': False,
                'message': 'Prediction failed. Please try again.',
                'class_index': -1
            }

_detector = None

def init_detector(model_path, class_indices_path):
    global _detector
    _detector = CropDiseaseDetector(model_path, class_indices_path)
    return _detector

def get_detector():
    return _detector