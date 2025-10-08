#!/usr/bin/env python3
"""
Simple metadata extractor that works immediately without large model downloads
Extracts basic image metadata and provides a foundation for classification
"""

import os
from PIL import Image
import sqlite3
import json
from datetime import datetime
import hashlib

def get_image_metadata(image_path):
    """Extract basic metadata from image file"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_type = img.format
            mode = img.mode

            # Get file stats
            stat = os.stat(image_path)
            file_size = stat.st_size
            created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
            modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

            return {
                'width': width,
                'height': height,
                'format': format_type,
                'color_mode': mode,
                'file_size_bytes': file_size,
                'created_time': created_time,
                'modified_time': modified_time
            }
    except Exception as e:
        return {'error': str(e)}

def analyze_filename(filename):
    """Analyze filename for potential military indicators"""
    name_lower = filename.lower()

    # Military equipment keywords in filenames
    military_terms = {
        'missile': ['missile', 'rocket', 'icbm', 'slbm'],
        'aircraft': ['jet', 'fighter', 'bomber', 'helicopter', 'drone', 'uav'],
        'vehicle': ['tank', 'apc', 'ifv', 'bmp', 'btr', 'tel'],
        'naval': ['ship', 'warship', 'destroyer', 'submarine', 'carrier']
    }

    detected_equipment = []
    for category, terms in military_terms.items():
        for term in terms:
            if term in name_lower:
                detected_equipment.append(f"{category}: {term}")
                break

    return detected_equipment

def setup_database(db_path="image_metadata.db"):
    """Setup SQLite database for metadata storage"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE NOT NULL,
        filepath TEXT,
        metadata TEXT,  -- JSON metadata
        filename_analysis TEXT,  -- JSON analysis
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("Database setup complete!")

def process_images(images_dir="images", db_path="image_metadata.db"):
    """Process all images and extract metadata"""

    setup_database(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get already processed images
    cursor.execute("SELECT filename FROM image_metadata")
    processed = {row[0] for row in cursor.fetchall()}

    # Find all images
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    images_to_process = []

    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root, file)
                if file not in processed:
                    images_to_process.append(full_path)

    print(f"Found {len(images_to_process)} images to process")

    processed_count = 0
    for image_path in images_to_process:
        filename = os.path.basename(image_path)

        # Extract metadata
        metadata = get_image_metadata(image_path)

        # Analyze filename
        filename_analysis = analyze_filename(filename)

        # Save to database
        metadata_json = json.dumps(metadata)
        analysis_json = json.dumps(filename_analysis)

        try:
            cursor.execute("""
            INSERT INTO image_metadata (filename, filepath, metadata, filename_analysis)
            VALUES (?, ?, ?, ?)
            """, (filename, image_path, metadata_json, analysis_json))

            processed_count += 1
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} images...")
                conn.commit()  # Commit every 100 images

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    conn.commit()
    conn.close()

    print(f"\nCompleted! Processed {processed_count} images.")
    print("Metadata saved to: image_metadata.db")

    # Show sample results
    show_sample_results(db_path)

def show_sample_results(db_path="image_metadata.db"):
    """Show sample results from the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM image_metadata")
    total_count = cursor.fetchone()[0]

    print(f"\n{'='*50}")
    print(f"DATABASE SUMMARY: {total_count} images processed")
    print(f"{'='*50}")

    # Show sample of processed images
    cursor.execute("""
    SELECT filename, metadata, filename_analysis
    FROM image_metadata
    LIMIT 5
    """)

    print("\nSAMPLE RESULTS:")
    for row in cursor.fetchall():
        filename, metadata_json, analysis_json = row
        metadata = json.loads(metadata_json)
        analysis = json.loads(analysis_json)

        print(f"\nFile: {filename}")
        print(f"   Size: {metadata.get('width', '?')}x{metadata.get('height', '?')} pixels")
        print(f"   Format: {metadata.get('format', '?')}")
        print(f"   File size: {metadata.get('file_size_bytes', 0) // 1024} KB")

        if analysis:
            print(f"   Filename analysis: {', '.join(analysis)}")
        else:
            print("   Filename analysis: No military indicators detected")

    conn.close()

if __name__ == "__main__":
    print("Military Image Metadata Extractor")
    print("=====================================")
    print("This tool extracts basic metadata from your images and analyzes filenames")
    print("for military equipment indicators. It works immediately without downloads!")
    print()

    process_images()
