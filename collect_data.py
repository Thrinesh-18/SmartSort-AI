"""
SmartSort-AI Data Collection Script
Guides manual collection and organizes data into train/val splits
"""

import os
import sys
import shutil
import random


def manual_collection_guide():
    """
    Instructions for manually collecting images
    """
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                SmartSort-Ai Image Collection Guide    ║
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


def organize_downloaded_data():
    """
    Organize data into train/val split from unorganized data folder
    """
    print("📁 Organizing data into train/val split...\n")

    source_dir = 'data'  # Source folder containing class subfolders

    if not os.path.exists(source_dir):
        print(f"❌ {source_dir} not found!")
        return False

    for split in ['train', 'val']:
        for cls in ['PET', 'HDPE', 'OTHER']:
            os.makedirs(f'data/{split}/{cls}', exist_ok=True)

    print("Processing images...")

    for cls in ['PET', 'HDPE', 'OTHER']:
        class_dir = os.path.join(source_dir, cls)

        if not os.path.exists(class_dir):
            print(f"⚠️  {class_dir} not found, skipping...")
            continue

        images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        random.shuffle(images)

        split_idx = int(len(images) * 0.8)
        train_images = images[:split_idx]
        val_images = images[split_idx:]

        for img in train_images:
            src = os.path.join(class_dir, img)
            dst = os.path.join('data/train', cls, img)
            shutil.copy2(src, dst)

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


def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║               SmartSort-Ai Data Collection Tool   ║
    ╚═══════════════════════════════════════════════════╝

    Choose a method:

    1. Manual collection guide (Best quality)
    2. Organize existing data into train/val split
    3. Exit
    """)

    choice = input("Enter choice (1-3): ").strip()

    if choice == '1':
        manual_collection_guide()

    elif choice == '2':
        organize_downloaded_data()

    elif choice == '3':
        print("👋 Goodbye!")
        sys.exit(0)

    else:
        print("❌ Invalid choice!")


if __name__ == '__main__':
    main()
