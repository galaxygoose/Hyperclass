#!/usr/bin/env python3
"""
Test script for multiple images with enhanced AI classification
"""

import os
from image_classifier import ImageClassifier

def test_multiple_images():
    """Test the enhanced classifier on multiple images"""

    # Create classifier
    print("Initializing classifier...")
    classifier = ImageClassifier()

    # Test on first few images
    images_dir = 'images'
    count = 0

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and count < 5:
                test_image = os.path.join(root, file)
                print(f'Testing: {file}')

                result = classifier.process_image(test_image)
                print(f'  Description: {result["description"]}')
                print(f'  Country: {result["country"]}')
                print(f'  Keywords: {result["keywords"][:5]}...')  # Show first 5 keywords
                print()
                count += 1
            if count >= 5:
                break
        if count >= 5:
            break

if __name__ == "__main__":
    test_multiple_images()
