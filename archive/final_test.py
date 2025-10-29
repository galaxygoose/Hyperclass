#!/usr/bin/env python3
"""
Final test of the enhanced Google Vision API system
"""

from google_vision_analyzer import GoogleVisionAnalyzer

def test_enhanced_system():
    """Test the complete enhanced system"""
    analyzer = GoogleVisionAnalyzer()

    # Test with a real image scenario
    test_result = analyzer.analyze_image('images/00005_033_6671362_6166ce61d4ac5.png')

    print("=== FINAL ENHANCED SYSTEM TEST ===")
    print(f"Description: {test_result['description']}")
    print(f"Country: {test_result['country']}")
    print(f"Keywords: {test_result['keywords']}")
    print(".3f")
    print(f"Source: {test_result['source_type']}")
    print(f"AI Generated: {test_result['metadata_is_ai']}")

    print("\n=== ANALYSIS ===")
    print(f"Vision labels found: {len(test_result['vision_labels'])}")
    print(f"Objects detected: {test_result['vision_objects']}")
    if test_result['extracted_text']:
        print(f"Text extracted: {test_result['extracted_text']}")

    return test_result

def main():
    """Main test function"""
    test_enhanced_system()

if __name__ == "__main__":
    main()
