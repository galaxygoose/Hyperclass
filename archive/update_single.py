#!/usr/bin/env python3
from google_vision_analyzer import GoogleVisionAnalyzer
import psycopg2
import os

def update_single_image():
    analyzer = GoogleVisionAnalyzer()

    # Test on the specific image
    test_filename = "16228_000_1WH70V.png"
    image_path = os.path.join("images", test_filename)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Analyzing: {test_filename}")

    # Get the analysis result
    analysis_result = analyzer.analyze_image(image_path)

    if analysis_result and 'description' in analysis_result:
        new_description = analysis_result['description']
        new_keywords = analysis_result.get('keywords', [])

        print(f"New description: '{new_description}'")
        print(f"Keywords: {new_keywords}")

        # Update database
        conn = psycopg2.connect(
            host='localhost',
            database='image_classification',
            user='postgres',
            password='class123',
            port=5433
        )
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE image_metadata
        SET description = %s, keywords = %s, processed_at = NOW()
        WHERE filename = %s
        """, (new_description, new_keywords, test_filename))

        conn.commit()
        cursor.close()
        conn.close()

        print("Database updated successfully")
    else:
        print("No analysis result")

if __name__ == "__main__":
    update_single_image()
