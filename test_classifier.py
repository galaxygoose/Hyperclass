#!/usr/bin/env python3
"""
Test script for the updated image classifier
"""

import os
from image_classifier import ImageClassifier

def test_classifier():
    """Test the updated classifier functionality"""

    # Create classifier
    print("Initializing classifier...")
    classifier = ImageClassifier()

    # Find a test image
    images_dir = 'images'
    test_image = None

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break

    if not test_image:
        print("No test image found!")
        return

    print(f"Testing on: {test_image}")

    # Process the image
    print("Processing image...")
    result = classifier.process_image(test_image)

    # Display results
    print("\nResults:")
    print(f"  Filename: {result['filename']}")
    print(f"  Description: {result['description']}")
    print(f"  Country: {result['country']}")
    print(f"  Keywords: {result['keywords']}")
    print(f"  Source Info: {result['source_info']}")
    print(f"  Success: {result['success']}")

if __name__ == "__main__":
    test_classifier()
