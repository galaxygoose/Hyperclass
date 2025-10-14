#!/usr/bin/env python3
"""
Debug the description generation issue
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def debug_description():
    """Debug the problematic description generation"""

    # Test with a specific problematic image
    analyzer = GoogleVisionAnalyzer()

    # Test the same image that gave weird results
    test_result = analyzer.analyze_image('images/24UFA_000_33UH7BD.png')

    print("=== DEBUGGING PROBLEMATIC DESCRIPTION ===")
    print(f"Description: {test_result['description']}")
    print(f"Country: {test_result['country']}")
    print(f"Equipment detected: {test_result.get('equipment', 'None')}")
    print(f"Objects detected: {test_result.get('objects', 'None')}")
    print(f"Keywords: {test_result['keywords']}")
    print(f"Vision labels: {test_result['vision_labels'][:10]}")

    # Also check what the Vision API raw data shows
    print("\n=== RAW VISION API ANALYSIS ===")
    api_key = analyzer.api_key
    if not api_key:
        print("No API key")
        return

    import requests
    import base64

    with open('images/24UFA_000_33UH7BD.png', 'rb') as f:
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

    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    try:
        response = requests.post(url, json=request_body, timeout=10)
        api_result = response.json()

        if response.status_code == 200 and api_result['responses']:
            response_data = api_result['responses'][0]
            labels = response_data.get('labelAnnotations', [])
            objects = response_data.get('localizedObjectAnnotations', [])

            print(f"\nVision API Labels ({len(labels)}):")
            for i, label in enumerate(labels[:10], 1):
                print(".3f")

            print(f"\nVision API Objects ({len(objects)}):")
            for i, obj in enumerate(objects[:5], 1):
                print(".3f")

    except Exception as e:
        print(f"API Error: {e}")

def main():
    """Main debug function"""
    debug_description()

if __name__ == "__main__":
    main()
