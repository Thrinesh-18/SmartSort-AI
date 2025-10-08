"""
PlasticNet Data Collection Script
Downloads sample images for training using Google Images or Kaggle
"""

import os
import sys
from pathlib import Path

# ============================================
# METHOD 1: Kaggle Dataset (RECOMMENDED)
# ============================================

def download_from_kaggle():
    """
    Download plastic waste dataset from Kaggle
    Requires: pip install kaggle
    """
    print("📥 Downloading from Kaggle...\n")
    
    try:
        import kaggle
        
        print("Step 1: Setting up Kaggle API...")
        print("(Make sure you have ~/.kaggle/kaggle.json configured)")
        
        # Download waste classification dataset
        dataset = 'techsash/waste-classification-data'
        print(f"\nDownloading: {dataset}")
        
        kaggle.api.dataset_download_files(
            dataset,
            path='data_kaggle',
            unzip=True
        )
        
        print("\n✅ Download complete!")
        print("📁 Files saved to: data_kaggle/")
        print("\n⚠️  Next step: Organize images into train/val folders")
        print("Run: python organize_data.py")
        
        return True
        
    except ImportError:
        print("❌ Kaggle not installed!")
        print("Install: pip install kaggle")
        print("Setup: https://github.com/Kaggle/kaggle-api#api-credentials")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================
# METHOD 2: Manual URLs (Quick & Simple)
# ============================================

def download_from_urls():
    """
    Download sample images from provided URLs
    """
    print("📥 Downloading sample images...\n")
    
    try:
        import requests
        from io import BytesIO
        from PIL import Image
    except ImportError:
        print("❌ Missing packages!")
        print("Install: pip install requests pillow")
        return False
    
    # Sample image URLs (replace with actual URLs)
    sample_urls = {
        'PET': [
            'https://example.com/pet1.jpg',
            'https://example.com/pet2.jpg',
            # Add more URLs
        ],
        'HDPE': [
            'https://example.com/hdpe1.jpg',
            # Add more URLs
        ],
        'OTHER': [
            'https://example.com/other1.jpg',
            # Add more URLs
        ]
    }
    
    for plastic_type, urls in sample_urls.items():
        output_dir = f'data/train/{plastic_type}'
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Downloading {plastic_type}...")
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                img.save(f'{output_dir}/sample_{i}.jpg')
                print(f"  ✅ Downloaded {i+1}/{len(urls)}")
            except Exception as e:
                print(f"  ❌ Failed: {url}")
    
    print("\n✅ Download complete!")
    return True

# ============================================
# METHOD 3: Manual Collection Guide
# ============================================

def manual_collection_guide():
    """
    Instructions for manually collecting images
    """
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         Manual Image Collection Guide                 ║
    ╚═══════════════════════════════════════════════════════╝
    
    📸 BEST OPTION: Take your own photos!
    
    Step 1: Find plastic items
    --------------------------------
    PET (#1):
      • Water bottles
      • Soda bottles  
      • Salad containers
      • Peanut butter jars
    
    HDPE (#2):
      • Milk jugs
      • Shampoo bottles
      • Detergent bottles
      • Yogurt containers
    
    OTHER (#7):
      • Mixed plastics
      • Food containers (check number)
      • Some beverage bottles
    
    Step 2: Take photos
    --------------------------------
    • Use your phone camera
    • Take 50-100 photos per type
    • Different angles, lighting
    • Various backgrounds
    • Include the recycling symbol if visible
    
    Step 3: Organize
    --------------------------------
    Save to:
      data/train/PET/    (80% of images)
      data/train/HDPE/
      data/train/OTHER/
      
      data/val/PET/      (20% of images)
      data/val/HDPE/
      data/val/OTHER/
    
    Step 4: Train
    --------------------------------
    python train_model.py
    
    ═══════════════════════════════════════════════════════
    
    💡 ALTERNATIVE: Download from Google Images
    ═══════════════════════════════════════════════════════
    
    Search terms:
      • "PET plastic bottle recycling symbol 1"
      • "HDPE plastic container recycling 2"
      • "plastic waste recycling number 7"
    
    Download 50-100 images per category
    Save to data/train/ and data/val/ folders
    """)

# ============================================
# DATA ORGANIZATION HELPER
# ============================================

def organize_downloaded_data():
    """
    Organize downloaded data into train/val split
    """
    print("📁 Organizing data into train/val split...\n")
    
    import shutil
    import random
    
    source_dir = 'data_kaggle'
    
    if not os.path.exists(source_dir):
        print(f"❌ {source_dir} not found!")
        return False
    
    # Create destination directories
    for split in ['train', 'val']:
        for cls in ['PET', 'HDPE', 'OTHER']:
            os.makedirs(f'data/{split}/{cls}', exist_ok=True)
    
    # Find and organize images
    print("Processing images...")
    
    for cls in ['PET', 'HDPE', 'OTHER']:
        class_dir = os.path.join(source_dir, cls.lower())
        
        if not os.path.exists(class_dir):
            print(f"⚠️  {class_dir} not found, skipping...")
            continue
        
        images = [f for f in os.listdir(class_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        random.shuffle(images)
        
        # 80-20 split
        split_idx = int(len(images) * 0.8)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        # Copy to train
        for img in train_images:
            src = os.path.join(class_dir, img)
            dst = os.path.join('data/train', cls, img)
            shutil.copy2(src, dst)
        
        # Copy to val
        for img in val_images:
            src = os.path.join(class_dir, img)
            dst = os.path.join('data/val', cls, img)
            shutil.copy2(src, dst)
        
        print(f"✅ {cls}: {len(train_images)} train, {len(val_images)} val")
    
    print("\n✅ Data organized!")
    print("📁 Train: data/train/")
    print("📁 Val: data/val/")
    print("\n🚀 Ready to train: python train_model.py")
    
    return True

# ============================================
# MAIN
# ============================================

def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║        PlasticNet Data Collection Tool            ║
    ╚═══════════════════════════════════════════════════╝
    
    Choose a method:
    
    1. Download from Kaggle (Recommended - 500+ images)
    2. Manual collection guide (Best quality)
    3. Organize downloaded data
    4. Exit
    """)
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        success = download_from_kaggle()
        if success:
            print("\nRun option 3 to organize the data!")
    
    elif choice == '2':
        manual_collection_guide()
    
    elif choice == '3':
        organize_downloaded_data()
    
    elif choice == '4':
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice!")

if __name__ == '__main__':
    main()