#!/usr/bin/env python3
"""
Test script for EXIF extraction and the full pipeline
"""

import os
from image_classifier import ImageClassifier

def test_exif_and_pipeline():
    """Test EXIF extraction and the full pipeline"""

    # Create classifier
    classifier = ImageClassifier()

    # Test EXIF extraction first
    test_image = "images/00005_033_6671362_6166ce61d4ac5.png"
    if os.path.exists(test_image):
        print("Testing EXIF extraction...")
        exif_data = classifier.extract_exif_data(test_image)
        print(f"EXIF data found: {sum(1 for v in exif_data.values() if v)} fields")
        for key, value in exif_data.items():
            if value:
                print(f"  {key}: {value}")

    # Test on 3 images to see the full pipeline
    images_dir = 'images'
    count = 0

    print('\n' + '=' * 80)
    print('Testing full pipeline on 3 images...')
    print('=' * 80)

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and count < 3:
                test_image = os.path.join(root, file)
                print(f'\n[Image {count+1}] {file}')
                print('-' * 40)

                result = classifier.process_image(test_image)
                print(f'Description: {result["description"]}')
                print(f'Country: {result["country"]}')
                print(f'Keywords: {result["keywords"][:3]}...')
                print(f'Metadata is AI: {result.get("metadata_is_ai", True)}')
                print(f'Source: {result.get("source_info", {}).get("source_type", "N/A")}')
                print(f'EXIF Camera Make: {result.get("exif_data", {}).get("camera_make", "N/A")}')
                count += 1
            if count >= 3:
                break
        if count >= 3:
            break

    print('\n' + '=' * 80)
    print('Test completed!')

if __name__ == "__main__":
    test_exif_and_pipeline()
