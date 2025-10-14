#!/usr/bin/env python3
"""
Test the final improved descriptions
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def test_improved_descriptions():
    """Test the improved description generation"""

    analyzer = GoogleVisionAnalyzer()

    test_images = [
        'images/24UFA_000_33UH7BD.png',  # Flag image (should be facilities)
        'images/24UEN_051_XxjpbeE000899_20181020_TPPFN0A001.png',  # Aircraft image
        'images/24j7e_000_32FF3TM.png'   # Tank image
    ]

    print("TESTING IMPROVED DESCRIPTIONS:")
    print("=" * 50)

    for image_path in test_images:
        if '24UFA' in image_path or '24UEN' in image_path or '24j7e' in image_path:
            result = analyzer.analyze_image(image_path)
            filename = image_path.split('/')[-1]
            print(f"\n{filename}:")
            print(f"  Description: {result['description']}")
            print(f"  Country: {result['country'] or 'None'}")
            print(f"  Objects: {result.get('objects', [])}")

def main():
    """Main test function"""
    test_improved_descriptions()

if __name__ == "__main__":
    main()
