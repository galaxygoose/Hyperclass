#!/usr/bin/env python3
"""
Test the enhanced Google Vision API system on specific news/media images
"""

import os
from google_vision_analyzer import GoogleVisionAnalyzer

def test_specific_images():
    """Test the enhanced system on the specified images"""

    # Test images as requested by user
    test_images = [
        '000_1CG7OJ_approved.png',  # Military equipment
        '000_1CY51T.png',          # Non-military corporate building
        '000_1DP1VF.png',          # Famous person?
        '000_1DN3Q6.png',          # Another image
        '000_1G11RG.png'           # Another image
    ]

    print("TESTING ENHANCED GOOGLE VISION API FOR NEWS/MEDIA")
    print("=" * 60)

    for image_filename in test_images:
        image_path = f"images/{image_filename}"

        if os.path.exists(image_path):
            print(f"\n{'='*20} {image_filename} {'='*20}")

            # Analyze with enhanced system
            analyzer = GoogleVisionAnalyzer()
            result = analyzer.analyze_image(image_path)

            print(f"Description: {result['description']}")
            print(f"Country: {result['country'] or 'None detected'}")
            print(f"People: {result['people']}")
            print(f"Locations: {result['locations']}")
            print(f"Organizations: {result['organizations']}")
            print(f"Objects: {result['objects']}")
            print(f"Keywords: {result['keywords'][:8]}...")  # Show first 8 keywords
            print(".3f")
        else:
            print(f"\n❌ Image not found: {image_path}")

def main():
    """Main test function"""
    test_specific_images()

if __name__ == "__main__":
    main()
