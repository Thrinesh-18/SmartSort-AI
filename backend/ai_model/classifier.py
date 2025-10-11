"""
SmartSort-AI Classifier - Production Inference Module
Loads trained model and provides prediction interface for FastAPI backend
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

class PlasticClassifier:
    """
    Wrapper class for PlasticNet model inference
    """
    
    # Class definitions
    CLASSES = {
        0: 'PET',
        1: 'HDPE',
        2: 'OTHER'
    }
    
    # Detailed material information
    MATERIAL_INFO = {
        'PET': {
            'full_name': 'Polyethylene Terephthalate',
            'recycling_code': '#1',
            'recyclability': 'High',
            'common_items': [
                'Water bottles',
                'Soda bottles', 
                'Food containers',
                'Peanut butter jars',
                'Salad containers'
            ],
            'value_per_kg': 0.12,
            'curbside_accepted': True,
            'instructions': 'Rinse clean, remove caps and labels, flatten bottles before recycling',
            'color': '#2E7D32',
            'tips': [
                '✅ Most widely recycled plastic worldwide',
                '♻️ Can be recycled into fleece, carpet, new bottles, and clothing',
                '⚠️ Remove labels if possible for better recycling',
                '💡 Look for the #1 symbol inside the recycling triangle'
            ],
            'environmental_impact': 'High recycling rate reduces oil consumption and landfill waste'
        },
        'HDPE': {
            'full_name': 'High-Density Polyethylene',
            'recycling_code': '#2',
            'recyclability': 'High',
            'common_items': [
                'Milk jugs',
                'Shampoo bottles',
                'Detergent bottles',
                'Motor oil containers',
                'Grocery bags'
            ],
            'value_per_kg': 0.18,
            'curbside_accepted': True,
            'instructions': 'Rinse thoroughly, caps can stay on, empty completely',
            'color': '#1976D2',
            'tips': [
                '✅ Second most recycled plastic - very valuable',
                '♻️ Recycled into plastic lumber, pipes, bottles, and toys',
                '💪 Very durable and easy to recycle',
                '💡 Identified by #2 inside recycling symbol'
            ],
            'environmental_impact': 'Highly recyclable, reduces need for virgin plastic production'
        },
        'OTHER': {
            'full_name': 'Other Plastics (Mixed)',
            'recycling_code': '#7',
            'recyclability': 'Variable',
            'common_items': [
                'Mixed plastic materials',
                'Some food containers',
                'Certain bottles',
                'Composite materials',
                'BPA-containing plastics'
            ],
            'value_per_kg': 0.02,
            'curbside_accepted': False,
            'instructions': 'Check with local facility - may need special drop-off location',
            'color': '#757575',
            'tips': [
                '⚠️ Recycling availability depends heavily on local facilities',
                '📍 May need specialized recycling center',
                '❓ Check for other recycling codes on the item',
                '🔍 Some #7 plastics are biodegradable, others are not'
            ],
            'environmental_impact': 'Mixed environmental impact - check local recycling options'
        }
    }
    
    def __init__(self, model_path='models/plastic_classifier.h5'):
        """
        Initialize classifier with trained model
        
        Args:
            model_path: Path to trained model file
        """
        self.model_path = model_path
        self.model = None
        self.img_size = (224, 224)
        self.model_loaded = False
        
    def load_model(self):
        """
        Load the trained TensorFlow model
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not os.path.exists(self.model_path):
            print(f"❌ Model file not found at: {self.model_path}")
            print("⚠️  Please train the model first: python train_model.py")
            return False
        
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            self.model_loaded = True
            print(f"✅ Model loaded successfully from {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def preprocess_image(self, image_data):
        """
        Preprocess image for model input
        
        Args:
            image_data: PIL Image, bytes, or file path
        
        Returns:
            numpy.ndarray: Preprocessed image array ready for prediction
        """
        # Handle different input types
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            image = Image.open(image_data)
        else:
            image = image_data
        
        # Convert to RGB if needed (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize(self.img_size)
        
        # Convert to array and normalize (0-1 range)
        img_array = np.array(image)
        img_array = img_array.astype('float32') / 255.0
        
        # Add batch dimension (model expects batch)
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image_data):
        """
        Predict plastic type from image
        
        Args:
            image_data: Image file (PIL Image, bytes, or file path)
        
        Returns:
            dict: Prediction results including all classification details
        """
        # Check if model is loaded
        if self.model is None:
            if not self.load_model():
                return {
                    'error': 'Model not loaded. Please train the model first.',
                    'success': False
                }
        
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_data)
            
            # Get predictions
            predictions = self.model.predict(processed_img, verbose=0)
            
            # Extract results
            class_probs = predictions[0]
            predicted_class_idx = np.argmax(class_probs)
            predicted_class = self.CLASSES[predicted_class_idx]
            confidence = float(class_probs[predicted_class_idx])
            
            # Get material info
            material_info = self.MATERIAL_INFO[predicted_class]
            
            # Build comprehensive result
            result = {
                'success': True,
                'predicted_class': predicted_class,
                'confidence': confidence,
                'confidence_percent': f"{confidence * 100:.1f}%",
                'full_name': material_info['full_name'],
                'recycling_code': material_info['recycling_code'],
                'recyclability': material_info['recyclability'],
                'common_items': material_info['common_items'],
                'value_per_kg': material_info['value_per_kg'],
                'curbside_accepted': material_info['curbside_accepted'],
                'instructions': material_info['instructions'],
                'tips': material_info['tips'],
                'color': material_info['color'],
                'environmental_impact': material_info['environmental_impact'],
                'all_probabilities': {
                    self.CLASSES[i]: float(class_probs[i])
                    for i in range(len(class_probs))
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def predict_batch(self, image_list):
        """
        Predict multiple images at once
        
        Args:
            image_list: List of images
        
        Returns:
            List of prediction dictionaries
        """
        results = []
        for image in image_list:
            results.append(self.predict(image))
        return results
    
    def get_confidence_interpretation(self, confidence):
        """
        Interpret confidence level
        
        Args:
            confidence: float between 0 and 1
            
        Returns:
            str: Human-readable interpretation
        """
        if confidence >= 0.9:
            return "Very High - Excellent prediction quality"
        elif confidence >= 0.75:
            return "High - Good prediction quality"
        elif confidence >= 0.6:
            return "Moderate - Acceptable prediction"
        elif confidence >= 0.4:
            return "Low - Consider retaking photo"
        else:
            return "Very Low - Please retake with better lighting/angle"


# ============================================
# TESTING UTILITY
# ============================================

def test_classifier():
    """
    Test the classifier with sample predictions
    """
    print("🧪 Testing PlasticNet Classifier...\n")
    
    classifier = PlasticClassifier()
    
    if not classifier.load_model():
        print("❌ Failed to load model. Train it first with: python train_model.py")
        return
    
    print("✅ Classifier ready for predictions!")
    print("\nModel Details:")
    print(f"  - Input size: {classifier.img_size}")
    print(f"  - Classes: {list(classifier.CLASSES.values())}")
    print(f"  - Model path: {classifier.model_path}")
    
    print("\n" + "="*60)
    print("Integration Example:")
    print("="*60)
    print("""
from backend.ai_model.classifier import PlasticClassifier

# Initialize classifier
classifier = PlasticClassifier()
classifier.load_model()

# Predict from image file
result = classifier.predict('path/to/image.jpg')

# Or from uploaded file (FastAPI)
image_bytes = await file.read()
result = classifier.predict(image_bytes)

# Print results
print(f"Plastic Type: {result['predicted_class']}")
print(f"Confidence: {result['confidence_percent']}")
print(f"Instructions: {result['instructions']}")
    """)
    print("="*60)


if __name__ == '__main__':
    test_classifier()