#!/usr/bin/env python3
"""
Test script for Google Vision API integration
"""

import os
import requests
import base64
from dotenv import load_dotenv

def test_api_connection():
    """Test Google Vision API connection"""
    print("=== GOOGLE VISION API CONNECTION TEST ===")

    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_CLOUD_API_KEY not found in .env file")
        return False

    print(f"API Key loaded: {len(api_key)} characters")

    # Create minimal test request (just base64 data, no prefix)
    test_image = '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=='

    request_body = {
        'requests': [{
            'image': {
                'content': test_image
            },
            'features': [{
                'type': 'LABEL_DETECTION',
                'maxResults': 1
            }]
        }]
    }

    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'

    try:
        print("Making API request...")
        response = requests.post(url, json=request_body, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: API request successful")
            return True
        else:
            print(f"ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return False

def test_real_image():
    """Test with a real image from the images directory"""
    print("\n=== REAL IMAGE TEST ===")

    # Find a test image
    test_image = None
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

    for root, dirs, files in os.walk('images'):
        for file in files:
            if file.lower().endswith(image_extensions):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break

    if not test_image:
        print("No test image found in images/ directory")
        return False

    print(f"Testing with image: {os.path.basename(test_image)}")

    # Read and analyze the image
    try:
        from google_vision_analyzer import GoogleVisionAnalyzer
        analyzer = GoogleVisionAnalyzer()

        result = analyzer.analyze_image(test_image)

        if result:
            print("SUCCESS: Image analysis completed")
            print(f"  Description: {result['description']}")
            print(f"  Country: {result['country'] or 'None detected'}")
            print(f"  Equipment: {', '.join(result['keywords'][:3])}")
            print(".3f")
            return True
        else:
            print("ERROR: No analysis result returned")
            return False

    except Exception as e:
        print(f"ERROR: Image analysis failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Google Vision API integration for military image classification")

    # Test API connection first
    if test_api_connection():
        print("\nAPI connection test: PASSED")

        # Test with real image
        if test_real_image():
            print("\nImage analysis test: PASSED")
            print("\n[SUCCESS] ALL TESTS PASSED! Google Vision API is ready to use.")
            print("\nNext steps:")
            print("1. Run 'python google_vision_classifier.py' to start processing")
            print("2. The system will only process NEW images not in your database")
            print("3. Existing 3,497 classifications will be preserved")
        else:
            print("\n[ERROR] Image analysis test failed")
    else:
        print("\n[ERROR] API connection test failed. Please check your setup:")
        print("1. Ensure GOOGLE_CLOUD_API_KEY is set in .env file")
        print("2. Enable Google Cloud Vision API in Google Cloud Console")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()
