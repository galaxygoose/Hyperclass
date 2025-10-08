#!/usr/bin/env python3
"""
Test script for the new pipeline on 5 images
"""

import os
from image_classifier import ImageClassifier

def test_5_images():
    """Test the new pipeline on 5 images"""

    # Create classifier
    classifier = ImageClassifier()

    # Test on first 5 images
    images_dir = 'images'
    count = 0

    print('Testing new pipeline on 5 images...')
    print('=' * 80)

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and count < 5:
                test_image = os.path.join(root, file)
                print(f'\n[Image {count+1}] {file}')
                print('-' * 40)

                result = classifier.process_image(test_image)
                print(f'Description: {result["description"]}')
                print(f'Country: {result["country"]}')
                print(f'Keywords: {result["keywords"][:3]}...')
                print(f'Metadata is AI: {result.get("metadata_is_ai", True)}')
                print(f'Source: {result.get("source_info", {}).get("source_type", "N/A")}')
                count += 1
            if count >= 5:
                break
        if count >= 5:
            break

    print('\n' + '=' * 80)
    print('Test completed!')

if __name__ == "__main__":
    test_5_images()
