#!/usr/bin/env python3
"""
Debug the enhanced people detection
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def debug_people_detection():
    """Debug the people detection system"""

    analyzer = GoogleVisionAnalyzer()

    # Test with a specific image
    result = analyzer.analyze_image('images/24UFA_000_33UH7BD.png')

    print("ENHANCED PEOPLE DETECTION DEBUG:")
    print("=" * 50)
    print(f"Faces detected: {result.get('vision_faces', 0)}")
    print(f"People detected: {result.get('people', [])}")
    print(f"Organizations: {result.get('organizations', [])}")
    print(f"Locations: {result.get('locations', [])}")
    print(f"Country: {result.get('country')}")
    print(f"Description: {result['description']}")

    # Also check the raw Vision API data
    print("\nRAW VISION API DATA:")
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
                {'type': 'FACE_DETECTION', 'maxResults': 20},
                {'type': 'WEB_DETECTION', 'maxResults': 10}
            ]
        }]
    }

    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    try:
        response = requests.post(url, json=request_body, timeout=10)
        api_result = response.json()

        if response.status_code == 200 and api_result['responses']:
            response_data = api_result['responses'][0]

            faces = response_data.get('faceAnnotations', [])
            web_detection = response_data.get('webDetection', {})

            print(f"\nFace Detection ({len(faces)} faces):")
            for i, face in enumerate(faces[:3], 1):
                print(f"  Face {i}:")
                if 'celebrity' in face:
                    print(f"    Celebrity: {face['celebrity'].get('name', 'Unknown')}")
                if 'name' in face:
                    print(f"    Name: {face['name']}")

            print(f"\nWeb Detection:")
            if 'webEntities' in web_detection:
                entities = web_detection['webEntities'][:5]
                print(f"  Web Entities ({len(entities)}):")
                for entity in entities:
                    print(f"    {entity.get('description', 'Unknown')}")

            if 'visuallySimilarImages' in web_detection:
                similar = web_detection['visuallySimilarImages'][:3]
                print(f"  Similar Images ({len(similar)}):")
                for img in similar:
                    if 'pageTitle' in img:
                        print(f"    {img['pageTitle']}")

    except Exception as e:
        print(f"API Error: {e}")

def main():
    """Main debug function"""
    debug_people_detection()

if __name__ == "__main__":
    main()
