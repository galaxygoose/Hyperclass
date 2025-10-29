#!/usr/bin/env python3
"""
Batch test the improved Google Vision analyzer on multiple images
"""

import os
from google_vision_analyzer import GoogleVisionAnalyzer

def batch_test_analyzer():
    """Test the analyzer on multiple sample images"""

    analyzer = GoogleVisionAnalyzer()

    # Test on the specified images
    test_images = [
        "0000D_000_9ZZ2ZB.png",
        "000_1A50EQ.png",
        "000_1A94WQ_approved.png",
        "000_1BD7CA.png",
        "000_1DF0EN_approved.png",
        "000_1DG47N.png",
        "000_1DF8HT.png"
    ]

    print("BATCH TESTING IMPROVED GOOGLE VISION ANALYZER")
    print("=" * 60)

    for image_name in test_images:
        image_path = os.path.join("images", image_name)

        if not os.path.exists(image_path):
            print(f"\n[NOT FOUND] Image not found: {image_name}")
            continue

        print(f"\n[ANALYZING] {image_name}")
        print("-" * 50)

        try:
            result = analyzer.analyze_image(image_path)

            if result and 'description' in result:
                description = result['description']
                print(f"Description: {description}")

                # Show keywords too
                if 'keywords' in result and result['keywords']:
                    keywords = result['keywords'][:5]  # Show first 5 keywords
                    print(f"Keywords: {', '.join(keywords)}")
                else:
                    print("Keywords: None")

                print("[SUCCESS] Analysis completed")
            else:
                print("[FAILED] Analysis failed - no result returned")

        except Exception as e:
            print(f"[ERROR] Analysis failed with error: {e}")

    print("\n" + "=" * 60)
    print("BATCH TEST COMPLETE")
    print("Review the descriptions above. If they're good, proceed with full re-analysis.")

if __name__ == "__main__":
    batch_test_analyzer()
