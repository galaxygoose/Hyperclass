#!/usr/bin/env python3
"""
Test the analyzer on the flag image
"""

import os
import base64
from google_vision_analyzer import GoogleVisionAnalyzer

def test_flag_image():
    """Test the analyzer on the American/Chinese flag image"""

    analyzer = GoogleVisionAnalyzer()

    image_name = "000_1BD7CA.png"
    image_path = os.path.join("images", image_name)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Analyzing: {image_name}")
    print("-" * 50)

    # First get raw Vision API data
    if analyzer.api_key:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        import requests
        request_body = {
            'requests': [{
                'image': {'content': image_data},
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 20},
                    {'type': 'OBJECT_LOCALIZATION', 'maxResults': 20},
                    {'type': 'TEXT_DETECTION', 'maxResults': 10},
                ]
            }]
        }

        url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
        response = requests.post(url, json=request_body, timeout=30)

        if response.status_code == 200:
            api_response = response.json()
            labels = api_response['responses'][0].get('labelAnnotations', [])
            if labels:
                print("RAW VISION LABELS:")
                for label in labels[:10]:
                    desc = label.get('description', '')
                    score = label.get('score', 0)
                    print(".3f")

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

if __name__ == "__main__":
    test_flag_image()
