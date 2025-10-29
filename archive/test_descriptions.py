#!/usr/bin/env python3
"""
Test enhanced photo descriptions and keywords for photolibrary use
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def test_enhanced_descriptions():
    """Test the enhanced description generation"""
    analyzer = GoogleVisionAnalyzer()

    # Simulate Vision API results for different scenarios
    test_cases = [
        {
            'name': 'Iranian Missile Display',
            'equipment': ['missile', 'TEL'],
            'countries': ['Iran'],
            'text': 'TEL 001'
        },
        {
            'name': 'Russian Tank Exercise',
            'equipment': ['tank'],
            'countries': ['Russia'],
            'text': ''
        },
        {
            'name': 'Chinese Fighter Jet',
            'equipment': ['fighter jet', 'military aircraft'],
            'countries': ['China'],
            'text': ''
        },
        {
            'name': 'US Naval Vessel',
            'equipment': ['warship'],
            'countries': ['United States'],
            'text': 'USS Nimitz'
        }
    ]

    print("=== ENHANCED PHOTO DESCRIPTIONS FOR PHOTOLIBRARY ===")

    for test in test_cases:
        print(f"\n--- {test['name']} ---")

        # Generate description
        description = analyzer._generate_description(
            test['equipment'], test['countries'], test['text']
        )
        print(f"Description: {description}")

        # Generate keywords
        keywords = analyzer._generate_photolibrary_keywords(
            test['equipment'], test['countries'], test['text'], []
        )
        print(f"Keywords: {keywords}")

    print("\n=== COMPARISON: OLD vs NEW ===")
    print("OLD: 'Military equipment image featuring soldier, military uniform'")
    print("NEW: 'Iran showcases missile capabilities during military demonstration'")
    print("     Keywords: ['missile', 'missile system', 'ballistic missile', 'iran', 'iran military']")

def main():
    """Main test function"""
    test_enhanced_descriptions()

if __name__ == "__main__":
    main()
