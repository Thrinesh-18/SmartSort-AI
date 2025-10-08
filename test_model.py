"""
Test PlasticNet Model
Quick testing script to verify your trained model works
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import sys
import os

# ============================================
# CONFIGURATION
# ============================================

MODEL_PATH = 'models/plastic_classifier.h5'
IMG_SIZE = (224, 224)

CLASSES = {
    0: 'PET (#1)',
    1: 'HDPE (#2)',
    2: 'OTHER (#7)'
}

# ============================================
# PREDICTION FUNCTION
# ============================================

def predict_image(model, image_path):
    """
    Predict plastic type from image file
    """
    # Load and preprocess image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img = img.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    
    # Get results
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    
    return class_idx, confidence, predictions[0]

# ============================================
# DISPLAY RESULTS
# ============================================

def display_results(image_path, class_idx, confidence, all_probs):
    """
    Pretty print prediction results
    """
    print("\n" + "="*60)
    print(f"📸 Image: {image_path}")
    print("="*60)
    
    print(f"\n✅ PREDICTION: {CLASSES[class_idx]}")
    print(f"🎯 Confidence: {confidence*100:.2f}%\n")
    
    print("All probabilities:")
    for i, prob in enumerate(all_probs):
        bar = "█" * int(prob * 50)
        print(f"  {CLASSES[i]:15} {bar} {prob*100:.1f}%")
    
    print("="*60)
    
    # Interpretation
    if confidence > 0.8:
        print("✅ High confidence - Good prediction!")
    elif confidence > 0.6:
        print("⚠️  Moderate confidence - Acceptable")
    else:
        print("❌ Low confidence - Image may be unclear")
    
    print()

# ============================================
# BATCH TESTING
# ============================================

def test_directory(model, directory):
    """
    Test all images in a directory
    """
    print(f"\n📂 Testing images in: {directory}\n")
    
    image_files = [f for f in os.listdir(directory) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("❌ No images found!")
        return
    
    results = []
    
    for img_file in image_files:
        img_path = os.path.join(directory, img_file)
        class_idx, confidence, probs = predict_image(model, img_path)
        
        results.append({
            'file': img_file,
            'prediction': CLASSES[class_idx],
            'confidence': confidence
        })
        
        print(f"✅ {img_file:30} → {CLASSES[class_idx]:15} ({confidence*100:.1f}%)")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    avg_confidence = np.mean([r['confidence'] for r in results])
    print(f"Total images: {len(results)}")
    print(f"Average confidence: {avg_confidence*100:.1f}%")
    
    # Breakdown by class
    print("\nPredictions breakdown:")
    for cls in CLASSES.values():
        count = sum(1 for r in results if r['prediction'] == cls)
        print(f"  {cls}: {count}")

# ============================================
# MAIN
# ============================================

def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║           PlasticNet Model Testing                ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found at: {MODEL_PATH}")
        print("Please train the model first: python train_model.py")
        sys.exit(1)
    
    # Load model
    print(f"📦 Loading model from: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model loaded successfully!\n")
    
    # Usage options
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_model.py <image_path>        - Test single image")
        print("  python test_model.py <directory>         - Test all images in directory")
        print("\nExample:")
        print("  python test_model.py test_images/bottle.jpg")
        print("  python test_model.py data/val/PET/")
        sys.exit(0)
    
    path = sys.argv[1]
    
    # Test single image or directory
    if os.path.isfile(path):
        class_idx, confidence, probs = predict_image(model, path)
        display_results(path, class_idx, confidence, probs)
    elif os.path.isdir(path):
        test_directory(model, path)
    else:
        print(f"❌ Path not found: {path}")
        sys.exit(1)

if __name__ == '__main__':
    main()