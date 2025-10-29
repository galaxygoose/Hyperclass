#!/usr/bin/env python3
"""
Test Google Lens-style web detection functionality
"""
from google_vision_analyzer import GoogleVisionAnalyzer
import os
import base64
import requests

def test_web_detection():
    """Test web detection on sample images"""
    analyzer = GoogleVisionAnalyzer()

    if not analyzer.api_key:
        print("ERROR: No API key found")
        return

    # Test images - mix of different types
    test_images = [
        'images/0000D_000_9ZZ2ZB.png',  # Submarine
        'images/000_1DF0EN_approved.png',  # Military
        'images/16228_000_1WH70V.png',  # Food (problematic)
    ]

    print("Testing Google Lens-style web detection...")
    print("=" * 60)

    for image_path in test_images:
        if not os.path.exists(image_path):
            print(f"Skipping {image_path} - file not found")
            continue

        filename = os.path.basename(image_path)
        print(f"\nTesting: {filename}")
        print("-" * 40)

        try:
            # Get full analysis
            result = analyzer.analyze_image(image_path)
            description = result.get('description', 'No description')

            print(f"Final description: '{description}'")

            # Now test web detection specifically
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Make direct API call to see web detection
            request_body = {
                'requests': [{
                    'image': {'content': image_data},
                    'features': [
                        {'type': 'WEB_DETECTION', 'maxResults': 10}
                    ]
                }]
            }

            url = f'https://vision.googleapis.com/v1/images:annotate?key={analyzer.api_key}'
            response = requests.post(url, json=request_body, timeout=30)

            if response.status_code == 200:
                api_result = response.json()
                web_detection = api_result['responses'][0].get('webDetection', {})

                print("Web Detection Results:")
                print(f"  Best guess labels: {[g.get('label') for g in web_detection.get('bestGuessLabels', [])]}")
                print(f"  Web entities: {[e.get('description') for e in web_detection.get('webEntities', [])[:3]]}")

                # Show more detailed web detection data
                full_matching = web_detection.get('fullMatchingImages', [])
                partial_matching = web_detection.get('partialMatchingImages', [])
                pages = web_detection.get('pagesWithMatchingImages', [])

                print(f"  Full matching images: {len(full_matching)}")
                if full_matching:
                    for i, img in enumerate(full_matching[:2]):
                        print(f"    {i+1}: {img.get('url', 'No URL')[:80]}...")

                print(f"  Partial matching images: {len(partial_matching)}")
                print(f"  Matching pages: {len(pages)}")

                if pages:
                    for i, page in enumerate(pages[:2]):
                        print(f"    Page {i+1}: {page.get('url', 'No URL')[:60]}...")
                        print(f"      Title: {page.get('pageTitle', 'No title')[:50]}...")

                # Test our web description extraction
                mock_labels = [('test', 0.8)]
                web_desc = analyzer._extract_web_description(web_detection, mock_labels)
                if web_desc:
                    print(f"  Extracted web description: '{web_desc}'")
                else:
                    print("  No web description extracted")
            else:
                print(f"  API Error: {response.status_code}")

        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "=" * 60)
    print("Web detection test complete!")

if __name__ == "__main__":
    test_web_detection()
