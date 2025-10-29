#!/usr/bin/env python3
"""
Test the improved detection logic on multiple images
"""

from google_vision_analyzer import GoogleVisionAnalyzer
import os

def test_improvements():
    """Test improved detection on multiple images"""
    analyzer = GoogleVisionAnalyzer()

    test_images = [
        'images/24UEN_051_XxjpbeE000899_20181020_TPPFN0A001.png',
        'images/24UAN_000_33L48HD.png',
        'images/24j7e_000_32FF3TM.png'  # This one had tank in the description earlier
    ]

    print("TESTING IMPROVED DETECTION:")
    print("=" * 50)

    for image_path in test_images[:2]:  # Test first 2
        if os.path.exists(image_path):
            result = analyzer.analyze_image(image_path)
            print(f"\nImage: {os.path.basename(image_path)}")
            print(f"Description: {result['description']}")
            print(f"Country: {result['country']}")
            print(f"Keywords: {result['keywords'][:3]}...")  # Show first 3 keywords
        else:
            print(f"Image not found: {image_path}")

def main():
    """Main test function"""
    test_improvements()

if __name__ == "__main__":
    main()
