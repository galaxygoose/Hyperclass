#!/usr/bin/env python3
"""
Test the analyzer on a specific image
"""

import os
import base64
from google_vision_analyzer import GoogleVisionAnalyzer

def test_specific_image():
    """Test the analyzer on the oil tanker image"""

    analyzer = GoogleVisionAnalyzer()

    image_name = "0000D_000_9ZZ2ZB.png"
    image_path = os.path.join("images", image_name)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Analyzing: {image_name}")
    print("-" * 50)

    # Get raw Vision API response
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
                    {'type': 'WEB_DETECTION', 'maxResults': 10}
                ]
            }]
        }

        url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
        response = requests.post(url, json=request_body, timeout=30)

        if response.status_code == 200:
            api_response = response.json()
            print("RAW VISION API DETECTIONS:")
            print("-" * 30)

            labels = api_response['responses'][0].get('labelAnnotations', [])
            if labels:
                print("Labels detected:")
                for label in labels[:10]:
                    desc = label.get('description', '')
                    score = label.get('score', 0)
                    print(".3f")

            objects = api_response['responses'][0].get('localizedObjectAnnotations', [])
            if objects:
                print("\nObjects detected:")
                for obj in objects[:5]:
                    name = obj.get('name', '')
                    score = obj.get('score', 0)
                    print(".3f")

            text_annotations = api_response['responses'][0].get('textAnnotations', [])
            if text_annotations:
                try:
                    text_desc = text_annotations[0]['description'][:100]
                    print(f"\nText detected: '{text_desc}...'")
                except UnicodeEncodeError:
                    print("\nText detected: [Unicode text - unable to display]")

    # Get analyzer result
    result = analyzer.analyze_image(image_path)

    if result and 'description' in result:
        description = result['description']
        print(f"\nGENERATED DESCRIPTION: {description}")

        # Debug: show what the analyzer detected
        print("\nANALYZER EXTRACTION:")
        print(f"People: {result.get('detected_people', [])}")
        print(f"Objects: {result.get('detected_objects', [])}")
        print(f"Locations: {result.get('detected_locations', [])}")
        print(f"Text: {result.get('detected_text', '')}")
    else:
        print("Analysis failed")

if __name__ == "__main__":
    test_specific_image()
