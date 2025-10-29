#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer
import os
import base64
import requests

def debug_vision_api():
    analyzer = GoogleVisionAnalyzer()

    # Test on the food image to see what labels it detects
    test_image = 'images/16228_000_1WH70V.png'
    if os.path.exists(test_image):
        print('Testing Vision API labels for food image...')

        # Read image and make direct API call to see raw labels
        with open(test_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        request_body = {
            'requests': [{
                'image': {'content': image_data},
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 10},
                    {'type': 'WEB_DETECTION', 'maxResults': 5}
                ]
            }]
        }

        url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
        response = requests.post(url, json=request_body, timeout=30)

        if response.status_code == 200:
            result = response.json()
            labels = result['responses'][0].get('labelAnnotations', [])
            print('Top labels:')
            for label in labels[:5]:
                print(f'  {label["description"]} ({label["score"]:.3f})')

            web_detection = result['responses'][0].get('webDetection', {})
            best_guess = web_detection.get('bestGuessLabels', [])
            if best_guess:
                print('Best guess labels:')
                for guess in best_guess:
                    print(f'  {guess["label"]}')

            web_entities = web_detection.get('webEntities', [])
            if web_entities:
                print('Web entities:')
                for entity in web_entities[:3]:
                    print(f'  {entity.get("description", "No description")}')
        else:
            print(f'API error: {response.status_code}')

    else:
        print('Test image not found')

if __name__ == "__main__":
    debug_vision_api()
