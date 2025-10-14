#!/usr/bin/env python3
"""
Smart Hybrid Classifier using Google Vision API
Only processes NEW images not in the PostgreSQL database
Preserves existing classifications
"""

import os
import psycopg2
import json
from datetime import datetime
from typing import Set, Dict, List, Optional
from google_vision_analyzer import GoogleVisionAnalyzer
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

class GoogleVisionClassifier:
    """Smart classifier that uses Google Vision API and preserves existing data"""

    def __init__(self, images_dir: str = "images"):
        self.images_dir = images_dir

        # Database connection parameters for PostgreSQL
        # Try multiple connection methods
        self.db_params_list = [
            {
                'host': 'localhost',
                'database': 'image_classification',  # Database containing image_metadata table
                'user': 'hyper',  # As specified by user
                'password': 'class123',
                'port': 5433
            },
            {
                'host': 'localhost',
                'database': 'image_classification',  # Database containing image_metadata table
                'user': 'postgres',
                'password': 'password',
                'port': 5433
            },
            {
                'host': 'localhost',
                'database': 'image_classification',  # Database containing image_metadata table
                'user': 'postgres',
                'password': '',
                'port': 5433
            }
        ]

        # Use the first working connection method
        self.db_params = None
        for params in self.db_params_list:
            if self.test_database_connection_params(params):
                self.db_params = params
                break

        if not self.db_params:
            print("[ERROR] Could not connect to PostgreSQL database with any credentials")
            print("Please check your database configuration")
            return

        # Initialize Google Vision analyzer
        self.vision_analyzer = GoogleVisionAnalyzer()

        # Test database connection
        self.test_database_connection()

        # Get existing processed images
        self.existing_images = self.get_processed_images()

    def test_database_connection_params(self, db_params: Dict) -> bool:
        """Test PostgreSQL database connection with specific parameters"""
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'image_metadata'
            );
            """)

            table_exists = cursor.fetchone()[0]

            if table_exists:
                print(f"[OK] Connected to PostgreSQL as user '{db_params['user']}'")

                # Get count of existing records
                cursor.execute("SELECT COUNT(*) FROM image_metadata;")
                count = cursor.fetchone()[0]
                print(f"[OK] Database contains {count} existing classifications")

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            return False

    def test_database_connection(self) -> bool:
        """Test PostgreSQL database connection"""
        if not self.db_params:
            return False

        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'image_metadata'
            );
            """)

            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("[OK] Connected to PostgreSQL database")
                print("[OK] 'image_metadata' table exists")

                # Get count of existing records
                cursor.execute("SELECT COUNT(*) FROM image_metadata;")
                count = cursor.fetchone()[0]
                print(f"[OK] Database contains {count} existing classifications")

            else:
                print("[ERROR] 'image_metadata' table does not exist")
                print("Please run setup_database.py first")
                return False

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            print("Please ensure PostgreSQL is running on port 5433")
            return False

    def get_processed_images(self) -> Set[str]:
        """Get set of already processed image filenames"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            cursor.execute("SELECT filename FROM image_metadata")
            processed = {row[0] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            print(f"[OK] Found {len(processed)} already processed images")
            return processed

        except Exception as e:
            print(f"[ERROR] Failed to get processed images: {e}")
            return set()

    def should_process_image(self, filename: str) -> bool:
        """Check if image should be processed (not in database)"""
        return filename not in self.existing_images

    def save_result(self, result: Dict) -> bool:
        """Save classification result to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Insert or update record
            cursor.execute("""
            INSERT INTO image_metadata (
                filename, description, country, keywords, source_url, source_type,
                original_title, metadata_is_ai, processed_at, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (filename)
            DO UPDATE SET
                description = EXCLUDED.description,
                country = EXCLUDED.country,
                keywords = EXCLUDED.keywords,
                source_type = EXCLUDED.source_type,
                metadata_is_ai = EXCLUDED.metadata_is_ai,
                processed_at = EXCLUDED.processed_at,
                status = EXCLUDED.status
            """, (
                result['filename'],
                result['description'],
                result['country'],
                result['keywords'],  # Comprehensive searchable keywords including people, locations, organizations, objects
                None,  # source_url - could be enhanced later
                result['source_type'],
                None,  # original_title
                result['metadata_is_ai'],
                datetime.now(),
                'processed'
            ))

            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"[ERROR] Failed to save result for {result['filename']}: {e}")
            return False

    def process_single_image(self, image_path: str) -> Optional[Dict]:
        """Process a single image with Google Vision API"""
        filename = os.path.basename(image_path)

        if not self.should_process_image(filename):
            print(f"[SKIP] {filename} - already processed")
            return None

        print(f"[PROCESSING] {filename} with Google Vision API...")

        try:
            # Analyze image with Google Vision API
            result = self.vision_analyzer.analyze_image(image_path)

            if result:
                # Save to database
                if self.save_result(result):
                    print(f"[SAVED] {result['description'][:60]}...")
                    if result['country']:
                        print(f"        Country: {result['country']}")
                    if result['keywords']:
                        print(f"        Equipment: {', '.join(result['keywords'][:3])}")
                    print(".3f")
                else:
                    print(f"[ERROR] Failed to save {filename}")

            return result

        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")
            return None

    def find_new_images(self) -> List[str]:
        """Find all images that haven't been processed yet"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        all_images = []
        new_images = []

        # Find all images in directory (including subdirectories)
        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if file.lower().endswith(image_extensions):
                    all_images.append(os.path.join(root, file))

        # Filter for new images only
        for image_path in all_images:
            filename = os.path.basename(image_path)
            if self.should_process_image(filename):
                new_images.append(image_path)

        print(f"[INFO] Found {len(all_images)} total images")
        print(f"[INFO] Found {len(new_images)} new images to process")

        return new_images

    def process_all_new_images(self, batch_size: int = 10) -> Dict:
        """Process all new images in batches"""
        new_images = self.find_new_images()

        if not new_images:
            print("[INFO] No new images to process!")
            return {'processed': 0, 'skipped': len(self.existing_images)}

        print(f"\n{'='*60}")
        print("GOOGLE VISION CLASSIFIER")
        print(f"New images to process: {len(new_images)}")
        print(".2f")
        print(f"{'='*60}")

        results = {
            'processed': 0,
            'skipped': len(self.existing_images),
            'failed': 0,
            'total_new': len(new_images)
        }

        for i, image_path in enumerate(new_images, 1):
            try:
                # Show progress every 5 images
                if i % 5 == 1:
                    filename = os.path.basename(image_path)
                    print(f"\n[PROGRESS] Processing {i}/{len(new_images)}: {filename[:40]}...")

                result = self.process_single_image(image_path)

                if result:
                    results['processed'] += 1
                else:
                    results['failed'] += 1

                # Small delay between requests to be respectful to API
                import time
                time.sleep(0.5)

            except Exception as e:
                print(f"[ERROR] Exception processing {image_path}: {e}")
                results['failed'] += 1

        # Show final statistics
        self.show_final_stats(results)
        return results

    def show_final_stats(self, results: Dict):
        """Show final processing statistics"""
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE!")
        print(f"New images processed: {results['processed']}")
        print(f"Previously processed: {results['skipped']}")
        print(f"Failed: {results['failed']}")
        print(".1f")
        print(f"{'='*60}")

        # Show sample of what was processed
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT filename, description, country, confidence
            FROM image_metadata
            WHERE source_type = 'Google Vision API'
            ORDER BY processed_at DESC
            LIMIT 3
            """)

            recent_results = cursor.fetchall()
            cursor.close()
            conn.close()

            if recent_results:
                print("\nRECENT GOOGLE VISION RESULTS:")
                for filename, desc, country, conf in recent_results:
                    print(f"  {filename[:30]}... ({conf:.2f})")
                    print(f"    {desc[:50]}...")
                    if country:
                        print(f"    Country: {country}")
                    print()

        except Exception as e:
            print(f"[ERROR] Failed to show recent results: {e}")

    def enhance_existing_image(self, filename: str) -> bool:
        """Re-analyze an existing image with Google Vision API for improved accuracy"""
        # Find the image file
        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if file == filename:
                    image_path = os.path.join(root, file)

                    print(f"[ENHANCING] {filename} with Google Vision API...")

                    try:
                        # Analyze with Vision API
                        result = self.vision_analyzer.analyze_image(image_path)

                        if result:
                            # Update existing record
                            if self.save_result(result):
                                print(f"[ENHANCED] {result['description'][:60]}...")
                                return True
                            else:
                                print(f"[ERROR] Failed to save enhanced result for {filename}")
                                return False

                    except Exception as e:
                        print(f"[ERROR] Failed to enhance {filename}: {e}")
                        return False

        print(f"[ERROR] Could not find file: {filename}")
        return False

    def test_vision_api(self) -> bool:
        """Test Google Vision API connection and functionality"""
        print("\n=== TESTING GOOGLE VISION API ===")

        # Test API connection
        if not self.vision_analyzer.test_connection():
            print("[ERROR] Google Vision API connection test failed")
            return False

        print("[OK] Google Vision API connection successful")

        # Find a test image (look for one that should be in existing data)
        test_image = None
        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    test_image = os.path.join(root, file)
                    break
            if test_image:
                break

        if test_image:
            print(f"[TESTING] Analyzing test image: {os.path.basename(test_image)}")
            result = self.vision_analyzer.analyze_image(test_image)

            if result:
                print("[OK] Test analysis successful:")
                print(f"  Description: {result['description']}")
                print(f"  Country: {result['country'] or 'None'}")
                print(f"  Keywords: {', '.join(result['keywords'][:3])}")
                print(".3f")
                return True

        print("[ERROR] No test image found")
        return False

    def search_by_description(self, search_term: str) -> List[Dict]:
        """Search images by description text, keywords, or other metadata"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Search in multiple fields for comprehensive results
            cursor.execute("""
            SELECT filename, description, country, keywords, processed_at
            FROM image_metadata
            WHERE LOWER(description) LIKE %s
               OR LOWER(country) LIKE %s
               OR %s = ANY(keywords)
               OR LOWER(filename) LIKE %s
            ORDER BY
                CASE
                    WHEN LOWER(description) LIKE %s THEN 1  -- Exact description match first
                    WHEN %s = ANY(keywords) THEN 2        -- Keyword match second
                    WHEN LOWER(country) LIKE %s THEN 3     -- Country match third
                    ELSE 4                                 -- Filename match last
                END,
                processed_at DESC
            """, (
                f'%{search_term}%', f'%{search_term}%', search_term, f'%{search_term}%',
                f'%{search_term}%', search_term, f'%{search_term}%'
            ))

            results = []
            for row in cursor.fetchall():
                result = {
                    'filename': row[0],
                    'description': row[1],
                    'country': row[2],
                    'keywords': row[3] if row[3] else [],
                    'processed_at': row[4]
                }
                results.append(result)

            cursor.close()
            conn.close()
            return results

        except Exception as e:
            print(f"Error searching database: {e}")
            return []

def main():
    """Main function"""
    print("Google Vision Smart Hybrid Classifier")
    print("Uses Google Vision API for new images only")
    print("Preserves existing PostgreSQL database classifications")
    print("=" * 60)

    # Initialize classifier
    classifier = GoogleVisionClassifier()

    # Test Vision API connection
    if not classifier.test_vision_api():
        print("[ERROR] Vision API test failed. Please check your API key.")
        return

    print("\n" + "=" * 60)

    # Ask user what they want to do
    print("Choose an option:")
    print("1. Process all new images (recommended)")
    print("2. Process specific image")
    print("3. Enhance existing image")
    print("4. Show database statistics")
    print("5. Search images by description text")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == '1':
        # Process all new images
        results = classifier.process_all_new_images()
        print(f"\nProcessed {results['processed']} new images")
        print(f"Skipped {results['skipped']} existing images")

    elif choice == '2':
        # Process specific image
        filename = input("Enter image filename: ").strip()
        image_path = None

        # Find the image
        for root, dirs, files in os.walk(classifier.images_dir):
            for file in files:
                if file == filename:
                    image_path = os.path.join(root, file)
                    break

        if image_path:
            result = classifier.process_single_image(image_path)
            if result:
                print(f"\nProcessed: {result['description']}")
        else:
            print(f"Image '{filename}' not found")

    elif choice == '3':
        # Enhance existing image
        filename = input("Enter filename to enhance: ").strip()
        if classifier.enhance_existing_image(filename):
            print(f"Enhanced {filename} with Google Vision API")
        else:
            print(f"Failed to enhance {filename}")

    elif choice == '4':
        # Show statistics
        processed = len(classifier.existing_images)
        print(f"\nDatabase contains {processed} processed images")

        try:
            conn = psycopg2.connect(**classifier.db_params)
            cursor = conn.cursor()

            # Show country breakdown
            cursor.execute("""
            SELECT country, COUNT(*) as count
            FROM image_metadata
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
            LIMIT 5
            """)

            print("\nTOP COUNTRIES:")
            for country, count in cursor.fetchall():
                print(f"  {country}: {count}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error getting statistics: {e}")

    elif choice == '5':
        # Search by description text
        search_term = input("Enter search term (e.g., 'aircraft', 'building', 'military'): ").strip().lower()

        if search_term:
            results = classifier.search_by_description(search_term)
            print(f"\nFound {len(results)} images matching '{search_term}':")

            for result in results[:10]:  # Show top 10 matches
                print(f"  {result['filename']}")
                print(f"    Description: {result['description'][:60]}...")
                if result['country']:
                    print(f"    Country: {result['country']}")
                if result['keywords']:
                    print(f"    Keywords: {', '.join(result['keywords'][:3])}")
                print()

            if len(results) > 10:
                print(f"... and {len(results) - 10} more matches")

        else:
            print("No search term provided")

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
