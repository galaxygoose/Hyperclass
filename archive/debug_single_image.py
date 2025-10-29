#!/usr/bin/env python3
"""
Debug script to show complete Vision API response for a single image
"""

import os
import requests
import base64
import json
from dotenv import load_dotenv
from google_vision_analyzer import GoogleVisionAnalyzer

# Load environment variables
load_dotenv()

def debug_complete_image(image_path):
    """Show complete Vision API analysis for one image"""

    print(f"=== COMPLETE ANALYSIS: {os.path.basename(image_path)} ===")

    # 1. Show our system's interpretation
    analyzer = GoogleVisionAnalyzer()
    result = analyzer.analyze_image(image_path)

    print("\nOUR SYSTEM'S INTERPRETATION:")
    print(f"Description: {result['description']}")
    print(f"Country: {result['country']}")
    print(f"Keywords: {result['keywords']}")
    print(".3f")
    print(f"Source: {result['source_type']}")

    # 2. Show raw Vision API data
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_CLOUD_API_KEY not found")
        return

    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    request_body = {
        'requests': [{
            'image': {'content': image_data},
            'features': [
                {'type': 'LABEL_DETECTION', 'maxResults': 50},
                {'type': 'OBJECT_LOCALIZATION', 'maxResults': 50},
                {'type': 'TEXT_DETECTION'},
                {'type': 'IMAGE_PROPERTIES'}
            ]
        }]
    }

    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    try:
        response = requests.post(url, json=request_body, timeout=15)
        api_result = response.json()

        if response.status_code == 200 and api_result['responses']:
            response_data = api_result['responses'][0]

            print("\nRAW VISION API DATA:")

            # Labels
            labels = response_data.get('labelAnnotations', [])
            print(f"\nLABEL DETECTION ({len(labels)} labels):")
            for i, label in enumerate(labels[:15], 1):  # Show top 15
                print(f"  {i}. {label['description']} (confidence: {label['score']:.3f})")

            # Objects
            objects = response_data.get('localizedObjectAnnotations', [])
            print(f"\nOBJECT LOCALIZATION ({len(objects)} objects):")
            for i, obj in enumerate(objects[:10], 1):  # Show top 10
                print(f"  {i}. {obj['name']} (confidence: {obj['score']:.3f})")

            # Text
            text_annotations = response_data.get('textAnnotations', [])
            if text_annotations:
                print(f"\nTEXT DETECTION ({len(text_annotations)} text elements):")
                for i, text in enumerate(text_annotations[:5], 1):  # Show top 5
                    print(f"  {i}. '{text['description']}' (confidence: {text['boundingPoly']['vertices'][0] if 'boundingPoly' in text else 'N/A'})")
            else:
                print("\nTEXT DETECTION: No text detected")

            # Show why our system made its decisions
            print("\nWHY THIS DESCRIPTION?")
            if not result['keywords'] or result['keywords'] == []:
                print("No military equipment detected above confidence threshold")
                print("Equipment list is empty, so using generic description")
            else:
                print(f"Detected equipment: {result['keywords']}")

            if not result['country']:
                print("No country flags detected")
            else:
                print(f"Detected country: {result['country']}")

        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {api_result}")

    except Exception as e:
        print(f"Request failed: {e}")

def main():
    """Test with a specific image"""
    # Use one of the problematic images
    test_image = 'images/24UFA_000_33UH7BD.png'

    if os.path.exists(test_image):
        debug_complete_image(test_image)
    else:
        print(f"Test image not found: {test_image}")

if __name__ == "__main__":
    main()
