#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer
import os
import base64
import requests

def check_cocaine_labels():
    analyzer = GoogleVisionAnalyzer()

    test_image = 'images/16228_000_1WH70V.png'
    if os.path.exists(test_image):
        print('Testing cocaine image labels...')

        with open(test_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        request_body = {
            'requests': [{
                'image': {'content': image_data},
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 15},
                    {'type': 'WEB_DETECTION', 'maxResults': 5}
                ]
            }]
        }

        url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
        response = requests.post(url, json=request_body, timeout=30)

        if response.status_code == 200:
            result = response.json()
            labels = result['responses'][0].get('labelAnnotations', [])
            print('All labels:')
            for label in labels[:10]:
                print(f'  {label["description"]} ({label["score"]:.3f})')

            web_detection = result['responses'][0].get('webDetection', {})
            print('Best guess:', [g.get('label') for g in web_detection.get('bestGuessLabels', [])])
            print('Web entities:', [e.get('description') for e in web_detection.get('webEntities', []) if e.get('description')])
        else:
            print(f'API error: {response.status_code}')

if __name__ == "__main__":
    check_cocaine_labels()
