#!/usr/bin/env python3
"""
Test the new search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_vision_classifier import GoogleVisionClassifier

def test_search():
    """Test the search functionality"""
    print("Testing Search Functionality")
    print("=" * 40)

    # Initialize classifier
    classifier = GoogleVisionClassifier()

    # Test different search terms
    search_terms = ['aircraft', 'building', 'military', 'huawei']

    for search_term in search_terms:
        print(f"\nSearching for: '{search_term}'")

        results = classifier.search_by_description(search_term)

        print(f"Found {len(results)} images")

        if results:
            print("Top 3 results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result['filename']}")
                print(f"     Description: {result['description'][:50]}...")
                print(f"     Country: {result['country'] or 'None'}")
                print(f"     Keywords: {result['keywords'][:3] if result['keywords'] else 'None'}")
                print()
        else:
            print("  No results found")

def main():
    """Main test function"""
    test_search()

if __name__ == "__main__":
    main()
