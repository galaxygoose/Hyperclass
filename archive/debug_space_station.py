#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer
import os
import base64
import requests

def debug_space_station():
    analyzer = GoogleVisionAnalyzer()

    # Test the specific space station image
    test_image = 'images/000_1AL8DD.png'
    if os.path.exists(test_image):
        print('Testing space station image...')
        result = analyzer.analyze_image(test_image)
        print('Description:', result.get('description', 'No description'))
        print('Keywords:', result.get('keywords', []))

        # Get raw Vision API data to see what web detection provides
        with open(test_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        request_body = {
            'requests': [{
                'image': {'content': image_data},
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 10},
                    {'type': 'WEB_DETECTION', 'maxResults': 10}
                ]
            }]
        }

        url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
        response = requests.post(url, json=request_body, timeout=30)

        if response.status_code == 200:
            data = response.json()
            web_detection = data['responses'][0].get('webDetection', {})

            print('\nWeb Detection Analysis:')
            print('Best guess labels:', [g.get('label') for g in web_detection.get('bestGuessLabels', [])])
            print('Web entities:', [e.get('description') for e in web_detection.get('webEntities', []) if e.get('description')])

            pages = web_detection.get('pagesWithMatchingImages', [])
            print(f'Pages with matches: {len(pages)}')
            for i, page in enumerate(pages[:3]):
                print(f'  Page {i+1}: {page.get("pageTitle", "No title")[:60]}...')
                print(f'    URL: {page.get("url", "No URL")[:80]}...')
        else:
            print(f'API Error: {response.status_code}')
    else:
        print('Test image not found')

if __name__ == "__main__":
    debug_space_station()
