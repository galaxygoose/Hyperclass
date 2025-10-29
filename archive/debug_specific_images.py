#!/usr/bin/env python3
"""
Debug script to see what Vision API detects in problematic images
"""

import os
import requests
import base64
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_image_labels(image_path):
    """Debug what Vision API detects in a specific image"""

    # Get API key
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_CLOUD_API_KEY not found")
        return

    # Read and encode image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Prepare Vision API request
    request_body = {
        'requests': [{
            'image': {
                'content': image_data
            },
            'features': [
                {
                    'type': 'LABEL_DETECTION',
                    'maxResults': 20
                },
                {
                    'type': 'OBJECT_LOCALIZATION',
                    'maxResults': 20
                }
            ]
        }]
    }

    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    try:
        response = requests.post(url, json=request_body, timeout=10)
        result = response.json()

        if response.status_code == 200 and result['responses']:
            response_data = result['responses'][0]
            labels = response_data.get('labelAnnotations', [])
            objects = response_data.get('localizedObjectAnnotations', [])

            print(f"\n=== DEBUGGING: {os.path.basename(image_path)} ===")
            print(f"Total labels: {len(labels)}")
            print("Top labels with confidence:")
            for label in labels[:10]:
                print(".3f")

            print(f"\nTotal objects: {len(objects)}")
            if objects:
                print("Detected objects:")
                for obj in objects[:5]:
                    print(".3f")

            # Check if any labels match our military keywords
            print("\nMilitary keyword matching:")
            military_keywords = [
                'missile', 'rocket', 'tank', 'aircraft', 'helicopter', 'drone',
                'warship', 'submarine', 'soldier', 'military', 'uniform'
            ]

            found_military = []
            for label in labels:
                label_desc = label['description'].lower()
                if any(keyword in label_desc for keyword in military_keywords):
                    found_military.append(label)

            if found_military:
                print("Military-related labels found:")
                for label in found_military:
                    print(".3f")
            else:
                print("No military-related labels found above confidence threshold")

            return labels, objects

    except Exception as e:
        print(f"ERROR: {e}")
        return [], []

def main():
    """Debug specific images from the database"""

    # Test with some of the problematic images
    problematic_images = [
        'images/24UFA_000_33UH7BD.png',
        'images/24UEN_051_XxjpbeE000899_20181020_TPPFN0A001.png',
        'images/24UAN_000_33L48HD.png'
    ]

    print("DEBUGGING PROBLEMATIC IMAGES")
    print("=" * 50)

    for image_path in problematic_images:
        if os.path.exists(image_path):
            debug_image_labels(image_path)
        else:
            print(f"Image not found: {image_path}")

if __name__ == "__main__":
    main()
