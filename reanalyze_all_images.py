#!/usr/bin/env python3
"""
Re-analyze all images with improved Google Vision analyzer
Updates only description and keywords columns, preserves all others
"""

import os
import psycopg2
from google_vision_analyzer import GoogleVisionAnalyzer
from typing import Dict, List
import time

class ImageReanalyzer:
    """Re-analyze images with improved analyzer, updating only description/keywords"""

    def __init__(self, images_dir: str):
        self.analyzer = GoogleVisionAnalyzer()
        self.images_dir = images_dir
        self.db_params = {
            'host': 'localhost',
            'database': 'image_classification',
            'user': 'postgres',
            'password': 'class123',
            'port': 5433
        }

    def get_all_image_files(self) -> List[str]:
        """Get all image files from the images directory"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        image_files = []

        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))

        return sorted(image_files)

    def reanalyze_all_images(self):
        """Re-analyze all images and update database"""

        # Get all images from filesystem
        image_files = self.get_all_image_files()
        print(f"Found {len(image_files)} image files to analyze")

        # Connect to database
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        # Get existing database records
        cursor.execute("SELECT id, filename FROM image_metadata ORDER BY id")
        db_records = {filename: row_id for row_id, filename in cursor.fetchall()}
        print(f"Found {len(db_records)} records in database")

        processed = 0
        updated = 0
        errors = 0

        for image_path in image_files:
            filename = os.path.basename(image_path)

            # Check if this image exists in database
            if filename not in db_records:
                print(f"Skipping {filename} - not found in database")
                continue

            row_id = db_records[filename]

            try:
                print(f"Analyzing {filename}...")

                # Analyze with improved analyzer
                analysis_result = self.analyzer.analyze_image(image_path)

                if analysis_result and 'description' in analysis_result:
                    new_description = analysis_result['description']
                    new_keywords = analysis_result.get('keywords', [])

                    # Update description, keywords, and processed_at timestamp for progress tracking
                    cursor.execute("""
                    UPDATE image_metadata
                    SET description = %s, keywords = %s, processed_at = NOW()
                    WHERE id = %s
                    """, (new_description, new_keywords, row_id))

                    updated += 1
                    print(f"  [UPDATED] '{new_description}' (keywords: {len(new_keywords)})")

                    # Commit every 10 images
                    if updated % 10 == 0:
                        conn.commit()
                        print(f"Committed {updated} updates so far")

                else:
                    print(f"  [FAILED] Failed to analyze {filename}")
                    errors += 1

            except Exception as e:
                print(f"  [ERROR] Error analyzing {filename}: {e}")
                errors += 1

            processed += 1

            # Rate limiting for Vision API
            time.sleep(1)

        # Final commit
        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*60)
        print("RE-ANALYSIS COMPLETE!")
        print(f"Total images processed: {processed}")
        print(f"Successfully updated: {updated}")
        print(f"Errors: {errors}")
        print("="*60)

        # Show some examples of improved descriptions
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT filename, description
        FROM image_metadata
        WHERE description LIKE '%Political%' OR description LIKE '%president%' OR description LIKE '%minister%'
        ORDER BY filename
        LIMIT 5
        """)

        examples = cursor.fetchall()
        if examples:
            print("\nImproved political descriptions:")
            for filename, desc in examples:
                print(f"  {filename}: {desc}")

        cursor.close()
        conn.close()

def run_test_batch(images_dir, num_images=10):
    """Run a test batch on a subset of images"""
    print(f"Running test batch on {num_images} images...")
    print("=" * 60)

    if not os.path.exists(images_dir):
        print(f"Error: Images directory '{images_dir}' not found")
        return

    # Create re-analyzer
    reanalyzer = ImageReanalyzer(images_dir)

    # Get first N image files for testing
    image_files = reanalyzer.get_all_image_files()[:num_images]

    # Connect to database
    conn = psycopg2.connect(**reanalyzer.db_params)
    cursor = conn.cursor()

    # Get existing database records
    cursor.execute("SELECT filename FROM image_metadata ORDER BY filename")
    db_records = {filename: True for (filename,) in cursor.fetchall()}

    processed = 0
    updated = 0

    for image_path in image_files:
        filename = os.path.basename(image_path)

        # Check if this image exists in database
        if filename not in db_records:
            print(f"Skipping {filename} - not found in database")
            continue

        try:
            print(f"Testing {filename}...")

            # Analyze with improved analyzer
            analysis_result = reanalyzer.analyzer.analyze_image(image_path)

            if analysis_result and 'description' in analysis_result:
                new_description = analysis_result['description']
                new_keywords = analysis_result.get('keywords', [])

                print(f"  Result: '{new_description}'")
                if new_keywords:
                    print(f"  Keywords: {new_keywords[:5]}")

                updated += 1

        except Exception as e:
            print(f"  [ERROR] Error analyzing {filename}: {e}")

        processed += 1

    cursor.close()
    conn.close()

    print("\n" + "="*60)
    print("TEST BATCH COMPLETE!")
    print(f"Tested {processed} images, {updated} successful analyses")
    print("="*60)

    # Ask user if they want to proceed with full analysis
    try:
        response = input("\nDo you want to proceed with full re-analysis of all images? (y/N): ")
        if response.lower() == 'y':
            return True
        else:
            print("Re-analysis cancelled by user.")
            return False
    except EOFError:
        # Non-interactive environment - proceed automatically for this demo
        print("Non-interactive environment detected. Proceeding with full re-analysis...")
        return True

def main():
    """Main function to re-analyze all images"""

    # Images directory
    images_dir = 'images'  # Assuming it's in the current directory

    if not os.path.exists(images_dir):
        print(f"Error: Images directory '{images_dir}' not found")
        return

    # Always run test batch first
    proceed = run_test_batch(images_dir, num_images=5)

    if not proceed:
        print("Re-analysis cancelled by user.")
        return

    print("\nProceeding with full re-analysis...")
    print("=" * 60)

    # Create re-analyzer (API key loaded automatically from environment)
    reanalyzer = ImageReanalyzer(images_dir)

    # Run re-analysis
    reanalyzer.reanalyze_all_images()

if __name__ == "__main__":
    main()
