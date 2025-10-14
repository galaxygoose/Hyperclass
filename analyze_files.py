#!/usr/bin/env python3
"""
Analyze file usage and categorize them for cleanup
"""

import os

# Current files in the project
current_files = [
    'activate_venv.bat',
    'check_databases.py',
    'check_results.py',
    'debug_vision.py',
    'export_results.py',
    'fast_classifier.py',
    'final_test.py',
    'git_setup.md',
    'google_vision_analyzer.py',
    'google_vision_classifier.py',
    'image_classifier_sqlite.py',
    'image_classifier.py',
    'query',
    'query_results.py',
    'quick_test.py',
    'README.md',
    'requirements.txt',
    'reverse_image_search.py',
    'run_classifier.bat',
    'setup_database.py',
    'setup_venv.py',
    'simple_metadata_extractor.py',
    'test_5_images.py',
    'test_classifier.py',
    'test_db_connection.py',
    'test_descriptions.py',
    'test_exif_and_pipeline.py',
    'test_google_vision.py',
    'test_multiple_images.py',
    'test_reverse_search.py',
    'USER_GUIDE.md'
]

# Categorize files based on current usage
legacy_obsolete = [
    'fast_classifier.py',           # Original CLIP fast classifier
    'image_classifier.py',          # Main CLIP classifier with BLIP-2
    'image_classifier_sqlite.py',   # SQLite version
    'run_classifier.bat',           # Windows batch for old system
    'check_results.py',             # Results checker for old system
    'export_results.py',            # Export for old SQLite DB
    'query_results.py',             # Query utility for old setup
    'simple_metadata_extractor.py', # Basic metadata (superseded)
    'test_5_images.py',             # Test for old system
    'test_classifier.py',           # Classifier test for old system
    'test_db_connection.py',        # DB connection test (superseded)
    'test_exif_and_pipeline.py',    # EXIF test (superseded)
    'test_multiple_images.py',      # Multiple image test (superseded)
    'test_reverse_search.py',       # Reverse search test (superseded)
    'quick_test.py',                # Quick test for old system
]

current_active = [
    'google_vision_analyzer.py',    # Google Vision API integration
    'google_vision_classifier.py',  # Main classifier with Google Vision
    'test_google_vision.py',        # Google Vision API test
    'debug_vision.py',              # Vision API debugging
    'final_test.py',                # System integration test
    'test_descriptions.py',         # Description enhancement test
    'check_databases.py',           # Database inspection utility
]

support_utility = [
    'setup_venv.py',                # Virtual environment setup
    'setup_database.py',            # Database setup
    'requirements.txt',             # Dependencies
    'reverse_image_search.py',      # Reverse search framework (optional)
    'activate_venv.bat',            # Windows venv activation
    'query',                        # Query script (utility)
]

documentation = [
    'README.md',                    # Main documentation
    'USER_GUIDE.md',                # Comprehensive user guide
    'git_setup.md',                 # Git setup guide
]

print("FILE USAGE ANALYSIS")
print("=" * 50)

print("\nCURRENTLY ACTIVE (Google Vision API System):")
for file in sorted(current_active):
    print(f"  ACTIVE: {file}")

print("\nSUPPORT & UTILITY FILES (Still Needed):")
for file in sorted(support_utility):
    print(f"  UTILITY: {file}")

print("\nDOCUMENTATION:")
for file in sorted(documentation):
    print(f"  DOCS: {file}")

print("\nLEGACY/OBSOLETE (Not Used Anymore):")
for file in sorted(legacy_obsolete):
    print(f"  OBSOLETE: {file}")

print("\nSUMMARY:")
print(f"  Active files: {len(current_active)}")
print(f"  Support files: {len(support_utility)}")
print(f"  Documentation: {len(documentation)}")
print(f"  Legacy files: {len(legacy_obsolete)}")
print(f"  Total files analyzed: {len(current_files)}")

print("\nRECOMMENDATIONS:")
print("  - Legacy files can be archived or deleted")
print("  - Keep support files for system maintenance")
print("  - Documentation should be kept for users")
print("  - Active files are the current working system")
