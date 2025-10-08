"""
PlasticNet - Transfer Learning Training (Fast Version)
Uses MobileNetV2 pre-trained weights + minimal fine-tuning
Works with small datasets (50+ images per class)
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import numpy as np

# ============================================
# CONFIGURATION
# ============================================

CLASSES = ['PET', 'HDPE', 'OTHER']
IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Smaller batch for small datasets
EPOCHS = 15      # Fewer epochs needed with transfer learning
LEARNING_RATE = 0.0001

# Data directories
TRAIN_DIR = 'data/train'
VAL_DIR = 'data/val'
MODEL_SAVE_PATH = 'models/plastic_classifier.h5'

# ============================================
# CREATE MODEL
# ============================================

def create_transfer_model():
    """
    Creates model using MobileNetV2 with transfer learning
    Only trains the top layers - base stays frozen
    """
    # Load MobileNetV2 with ImageNet weights (frozen)
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(*IMG_SIZE, 3)
    )
    
    # Freeze all base layers
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
    x = Dropout(0.5)(x)
    predictions = Dense(3, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    print("✅ Model created with MobileNetV2 backbone")
    print(f"📊 Trainable parameters: {model.count_params():,}")
    
    return model

# ============================================
# DATA AUGMENTATION (AGGRESSIVE)
# ============================================

def create_data_generators():
    """
    Heavy augmentation to maximize small datasets
    """
    # Aggressive training augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator

# ============================================
# TRAIN
# ============================================

def train():
    """
    Fast training with transfer learning
    """
    print("\n🚀 Starting PlasticNet Transfer Learning Training\n")
    
    # Create model
    model = create_transfer_model()
    
    # Prepare data
    print("\n📊 Loading data...")
    train_gen, val_gen = create_data_generators()
    
    print(f"✅ Training samples: {train_gen.samples}")
    print(f"✅ Validation samples: {val_gen.samples}")
    print(f"✅ Classes: {list(train_gen.class_indices.keys())}\n")
    
    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        )
    ]
    
    # Train
    print("🔥 Training started...\n")
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate
    print("\n📊 Final Evaluation:")
    loss, acc = model.evaluate(val_gen)
    print(f"✅ Validation Accuracy: {acc*100:.2f}%")
    print(f"📁 Model saved to: {MODEL_SAVE_PATH}")
    
    return model, history

# ============================================
# OPTIONAL: Download Sample Dataset
# ============================================

def download_sample_dataset():
    """
    Downloads a small sample plastic dataset from Kaggle
    Requires: pip install kaggle
    """
    print("📥 Downloading sample plastic waste dataset...")
    
    # You'll need Kaggle API credentials
    # Instructions: https://github.com/Kaggle/kaggle-api
    
    try:
        import kaggle
        
        # Download plastic waste dataset
        kaggle.api.dataset_download_files(
            'techsash/waste-classification-data',
            path='data_raw',
            unzip=True
        )
        
        print("✅ Dataset downloaded to data_raw/")
        print("⚠️ You'll need to organize it into train/val folders")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManual option:")
        print("1. Download from: https://www.kaggle.com/datasets/techsash/waste-classification-data")
        print("2. Organize into data/train and data/val folders")

# ============================================
# QUICK SETUP HELPER
# ============================================

def quick_setup():
    """
    Creates directory structure for you
    """
    print("📁 Setting up directory structure...\n")
    
    dirs = [
        'data/train/PET',
        'data/train/HDPE',
        'data/train/OTHER',
        'data/val/PET',
        'data/val/HDPE',
        'data/val/OTHER',
        'models'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ Created: {d}")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Add images to data/train/[PET|HDPE|OTHER]/ folders")
    print("   - At least 50 images per class recommended")
    print("   - More is better (100-200 per class)")
    print("\n2. Add 20% of images to data/val/ for validation")
    print("\n3. Run: python train_model.py")
    print("="*60)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    import sys
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║      PlasticNet Transfer Learning Training        ║
    ║    Fast training with MobileNetV2 backbone        ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Check if setup needed
    if not os.path.exists('data/train'):
        print("⚠️  Data directories not found!\n")
        choice = input("Setup directories now? (y/n): ").lower()
        if choice == 'y':
            quick_setup()
            print("\n✅ Setup complete! Add your images and run again.")
            sys.exit(0)
        else:
            print("❌ Please create data/train and data/val directories first")
            sys.exit(1)
    
    # Check if images exist
    train_exists = any(os.listdir(f'data/train/{cls}') for cls in CLASSES if os.path.exists(f'data/train/{cls}'))
    
    if not train_exists:
        print("⚠️  No training images found!")
        print("\nOptions:")
        print("1. Add your own images to data/train/")
        print("2. Download sample dataset (requires Kaggle API)")
        
        choice = input("\nDownload sample dataset? (y/n): ").lower()
        if choice == 'y':
            download_sample_dataset()
        sys.exit(0)
    
    # Start training
    model, history = train()
    
    print("\n🎉 Training complete!")
    print(f"✅ Model ready at: {MODEL_SAVE_PATH}")
    print("\nNext: Test with test_model.py or integrate with backend!")