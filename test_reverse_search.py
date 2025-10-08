#!/usr/bin/env python3
"""
Test script for reverse image search functionality
"""

import os
import sys
from reverse_image_search import ReverseImageSearch

def test_reverse_search():
    """Test the reverse image search functionality"""

    # Find a test image
    images_dir = "images"
    if not os.path.exists(images_dir):
        print(f"Images directory '{images_dir}' not found!")
        return

    # Get list of image files
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    image_files = []

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(root, file))
                break  # Just get the first image for testing

    if not image_files:
        print("No images found for testing!")
        return

    test_image = image_files[0]
    print(f"Testing reverse image search on: {test_image}")

    # Initialize reverse image search
    reverse_search = ReverseImageSearch()

    try:
        # Test reverse image search
        print("Performing reverse image search...")
        results = reverse_search.search_and_extract_metadata(test_image, max_results=2)

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Description: {result.get('description', 'N/A')}")
            print(f"  Source: {result.get('source', 'N/A')}")

        # Test metadata extraction if we have results
        if results:
            best_result = results[0]
            if best_result.get('url'):
                print(f"\nTesting metadata extraction from: {best_result['url']}")
                metadata = reverse_search.extract_metadata_from_url(best_result['url'])
                print(f"Extracted metadata: {metadata}")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        reverse_search.cleanup()

if __name__ == "__main__":
    test_reverse_search()
