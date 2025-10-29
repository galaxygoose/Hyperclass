#!/usr/bin/env python3
"""
Debug script to see what Vision API is actually detecting
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def debug_vision_results():
    """Debug what the Vision API is detecting"""
    analyzer = GoogleVisionAnalyzer()

    # Test with the same image that showed generic results
    test_result = analyzer.analyze_image('images/00005_033_6671362_6166ce61d4ac5.png')

    print("=== DEBUGGING VISION API RESULTS ===")
    print(f"Description: {test_result['description']}")
    print(f"Country: {test_result['country']}")
    print(f"Keywords: {test_result['keywords']}")
    print(".3f")
    print()
    print("RAW VISION API DATA:")
    print(f"Vision labels: {test_result['vision_labels']}")
    print(f"Vision objects: {test_result['vision_objects']}")
    print(f"Extracted text: '{test_result['extracted_text']}'")

    # Let's also check what equipment was detected during processing
    print()
    print("DEBUGGING EQUIPMENT DETECTION:")

    # Simulate the detection process to see what equipment gets identified
    from PIL import Image
    import requests
    import base64
    import json

    # Read image and call Vision API directly
    with open('images/00005_033_6671362_6166ce61d4ac5.png', 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    request_body = {
        'requests': [{
            'image': {'content': image_data},
            'features': [
                {'type': 'LABEL_DETECTION', 'maxResults': 20},
                {'type': 'OBJECT_LOCALIZATION', 'maxResults': 20}
            ]
        }]
    }

    url = f"https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}"
    response = requests.post(url, json=request_body, timeout=10)
    result = response.json()

    if response.status_code == 200 and result['responses']:
        response_data = result['responses'][0]
        labels = response_data.get('labelAnnotations', [])
        objects = response_data.get('localizedObjectAnnotations', [])

        print(f"Total labels: {len(labels)}")
        print("Top labels:")
        for label in labels[:10]:
            print(f"  {label['description']} (confidence: {label['score']:.3f})")

        print(f"Total objects: {len(objects)}")
        if objects:
            print("Detected objects:")
            for obj in objects[:5]:
                print(f"  {obj['name']} (confidence: {obj['score']:.3f})")

def main():
    """Main debug function"""
    debug_vision_results()

if __name__ == "__main__":
    main()
