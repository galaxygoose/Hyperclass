#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer

analyzer = GoogleVisionAnalyzer()

# Test the filtering function
test_cases = [
    'pickup truck',  # Should reject - contains common single word
    'Russian military submarine',  # Should accept - English, substantial
    'National flag display',  # Should accept - English, substantial
    'food',  # Should reject - single common word
    'Military personnel in uniform',  # Should accept
    'CAR',  # Should reject - all caps
    'A very long description about military equipment',  # Should accept
    'image',  # Should reject - generic term
    'Beverly Boy Productions',  # Should reject - company name
    'Russian navy ireland',  # Should reject - concatenated
    'Aerial photography',  # Should reject - generic photography term
    'Fast attack craft',  # Should accept - military vessel
    'Chinese space station Tiangong',  # Should accept
    'Shoot rifle.',  # Should reject - imperative/command
    'Photo of tie in formal attire.',  # Should accept - proper description
    'rifle gun',  # Should reject - noun + noun
    'tie suit',  # Should reject - noun + noun
]

print("Testing description filtering:")
print("=" * 50)

for test in test_cases:
    result = analyzer._is_good_description(test)
    status = "ACCEPT" if result else "REJECT"
    print(f"{status}: '{test}'")
