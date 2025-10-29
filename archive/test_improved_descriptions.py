#!/usr/bin/env python3
"""
Test the improved Google Vision analyzer descriptions
"""

import os
import base64
from google_vision_analyzer import GoogleVisionAnalyzer

def test_improved_analyzer():
    """Test the improved analyzer on a few sample images"""

    # Initialize analyzer
    analyzer = GoogleVisionAnalyzer()

    # Test on a few images from the database
    test_images = [
        "00014_017_111070.png",  # Political figure
        "0000K_000_1MD5UO.png",  # Garmin GPS example
        "0001K_shutterstock_2133739611.png",  # Starlink
    ]

    print("Testing improved Google Vision analyzer descriptions:")
    print("="*60)

    for image_name in test_images:
        image_path = os.path.join("images", image_name)

        if os.path.exists(image_path):
            print(f"\nAnalyzing: {image_name}")
            print("-" * 40)

            # Get the raw Vision API response to see what's actually detected
            if analyzer.api_key:
                # Read and encode image
                with open(image_path, 'rb') as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')

                # Prepare Vision API request
                request_body = {
                    'requests': [{
                        'image': {'content': image_data},
                        'features': [
                            {'type': 'LABEL_DETECTION', 'maxResults': 20},
                            {'type': 'OBJECT_LOCALIZATION', 'maxResults': 20},
                            {'type': 'TEXT_DETECTION', 'maxResults': 10},
                            {'type': 'FACE_DETECTION', 'maxResults': 10},
                            {'type': 'WEB_DETECTION', 'maxResults': 10}
                        ]
                    }]
                }

                import requests
                url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
                response = requests.post(url, json=request_body, timeout=30)

                if response.status_code == 200:
                    api_response = response.json()
                    print("RAW VISION API DETECTIONS:")
                    print("-" * 30)

                    # Show labels
                    labels = api_response['responses'][0].get('labelAnnotations', [])
                    if labels:
                        print("Labels detected:")
                        for label in labels[:10]:
                            desc = label.get('description', '')
                            score = label.get('score', 0)
                            print(".3f")

                    # Show objects
                    objects = api_response['responses'][0].get('localizedObjectAnnotations', [])
                    if objects:
                        print("\nObjects detected:")
                        for obj in objects[:5]:
                            name = obj.get('name', '')
                            score = obj.get('score', 0)
                            print(".3f")

                    # Show text
                    text_annotations = api_response['responses'][0].get('textAnnotations', [])
                    if text_annotations:
                        print(f"\nText detected: '{text_annotations[0]['description'][:100]}...'")

                    # Show web detection
                    web_detection = api_response['responses'][0].get('webDetection', {})
                    if 'webEntities' in web_detection and web_detection['webEntities']:
                        print("\nWeb entities detected:")
                        for entity in web_detection['webEntities'][:5]:
                            score = entity.get('score', 0)
                            desc = entity.get('description', '')
                            print(".3f")

            # Now show the analyzer result
            result = analyzer.analyze_image(image_path)

            if result and 'description' in result:
                description = result['description']
                print(f"\nGENERATED DESCRIPTION: {description}")
            else:
                print("Analysis failed")
        else:
            print(f"Image not found: {image_path}")

if __name__ == "__main__":
    test_improved_analyzer()
