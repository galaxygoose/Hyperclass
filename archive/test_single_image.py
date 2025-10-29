#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer
import os

def test_single_image():
    analyzer = GoogleVisionAnalyzer()

    # Test on one of the problematic images the user mentioned
    test_filename = "16228_000_1WH70V.png"  # "Scene featuring food"
    image_path = os.path.join("images", test_filename)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Analyzing: {test_filename}")
    print("-" * 50)

    # Get the analysis result
    analysis_result = analyzer.analyze_image(image_path)

    if analysis_result and 'description' in analysis_result:
        description = analysis_result['description']
        keywords = analysis_result.get('keywords', [])

        print(f"Generated description: '{description}'")
        print(f"Keywords: {keywords}")
    else:
        print("No analysis result")

if __name__ == "__main__":
    test_single_image()
