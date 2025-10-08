#!/usr/bin/env python3
"""
Fast Military Image Classifier using CLIP (no BLIP-2 for speed)
"""

import os
from PIL import Image
import sqlite3
from transformers import CLIPProcessor, CLIPModel
import torch
from tqdm import tqdm
import json
import gc
import warnings
warnings.filterwarnings("ignore")

class FastImageClassifier:
    def __init__(self, images_dir="images", db_path="fast_classification.db"):
        self.images_dir = images_dir
        self.db_path = db_path

        # Initialize CLIP (fast model)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[SYSTEM] Using device: {self.device}")
        print("[SYSTEM] Initializing CLIP model for fast classification...")

        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        print("[OK] CLIP model loaded successfully!")

        # Military keywords database
        self.military_keywords = [
            # Missiles and Rockets
            "missile", "rocket", "ballistic missile", "cruise missile", "ICBM", "SLBM",
            "TEL", "Transporter Erector Launcher", "missile launcher", "SCUD", "SS-21",
            "SS-26", "Fateh-110", "Shahab", "Sejjil", "Qiam",

            # Aircraft
            "fighter jet", "military aircraft", "bomber", "helicopter", "drone", "UAV",
            "F-35", "F-22", "Su-35", "MiG-29", "J-20", "F-15", "F-16", "A-10",
            "B-52", "Tu-95", "Il-76", "C-130", "AH-64 Apache", "Mi-24",

            # Ground Vehicles
            "tank", "armored vehicle", "APC", "IFV", "artillery", "self-propelled artillery",
            "T-72", "T-90", "M1 Abrams", "Leopard 2", "Challenger 2", "Type 99",
            "BMP", "BTR", "Bradley", "Stryker", "MT-LB",

            # Naval
            "warship", "destroyer", "frigate", "submarine", "aircraft carrier",
            "cruiser", "corvette", "patrol boat", "USS", "HMS", "INS",

            # Other Military Equipment
            "radar", "anti-aircraft", "SAM", "surface-to-air missile", "Buk", "S-300",
            "S-400", "Patriot", "Iron Dome", "David's Sling", "THAAD",
            "nuclear weapon", "bomb", "munition", "explosive",

            # Personnel and Formations
            "soldier", "military uniform", "parade", "military ceremony", "general",
            "commander", "president", "world leader", "dictator", "monarch"
        ]

        # Country categories
        self.country_categories = [
            "United States", "Russia", "China", "North Korea", "Iran", "Israel",
            "Ukraine", "United Kingdom", "France", "Germany", "Japan", "India",
            "Syria", "Iraq", "Afghanistan", "Pakistan", "Turkey", "Saudi Arabia",
            "Egypt", "Lebanon", "Gaza Strip", "Taiwan", "South Korea", "Vietnam",
            "Cuba", "Venezuela", "Brazil", "Mexico", "Canada", "Australia"
        ]

        # Setup database
        self.setup_database()

    def setup_database(self):
        """Setup SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            description TEXT,
            country TEXT,
            keywords TEXT,
            confidence REAL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filename ON classifications(filename);")
        conn.commit()
        conn.close()

    def get_processed_images(self):
        """Get list of already processed images"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM classifications")
            processed = {row[0] for row in cursor.fetchall()}
            cursor.close()
            conn.close()
            return processed
        except:
            return set()

    def classify_image(self, image_path):
        """Classify a single image using CLIP"""
        try:
            image = Image.open(image_path).convert('RGB')
            filename = os.path.basename(image_path)

            # Create classification texts
            equipment_texts = [f"photo of {keyword} in military setting" for keyword in self.military_keywords[:30]]  # Limit for speed
            country_texts = [f"flag of {country}" for country in self.country_categories] + \
                           [f"military equipment from {country}" for country in self.country_categories[:10]]  # Limit for speed

            all_texts = equipment_texts + country_texts

            # Process with CLIP
            inputs = self.clip_processor(text=all_texts, images=image, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0]

            # Extract results
            detected_keywords = []
            detected_countries = []

            for i, prob in enumerate(probs):
                if prob > 0.15:  # Confidence threshold
                    text = all_texts[i]
                    if i < len(equipment_texts):
                        # This is equipment
                        keyword = self.military_keywords[i % len(self.military_keywords[:30])]
                        detected_keywords.append(keyword)
                    else:
                        # This is country
                        country_idx = (i - len(equipment_texts)) % len(self.country_categories)
                        country = self.country_categories[country_idx]
                        if country not in detected_countries:
                            detected_countries.append(country)

            # Generate description based on detections
            if detected_keywords and detected_countries:
                description = f"Military image showing {', '.join(detected_keywords[:2])} associated with {detected_countries[0]}"
            elif detected_keywords:
                description = f"Military equipment image featuring {', '.join(detected_keywords[:3])}"
            elif detected_countries:
                description = f"Military or national imagery associated with {detected_countries[0]}"
            else:
                description = "Military or defense-related image"

            # Calculate overall confidence
            max_confidence = float(torch.max(probs))

            return {
                'filename': filename,
                'description': description,
                'country': detected_countries[0] if detected_countries else None,
                'keywords': detected_keywords[:5],  # Limit to top 5
                'confidence': max_confidence,
                'success': True
            }

        except Exception as e:
            return {
                'filename': os.path.basename(image_path),
                'description': f"Classification failed: {str(e)}",
                'country': None,
                'keywords': [],
                'confidence': 0.0,
                'success': False
            }

    def save_result(self, result):
        """Save classification result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
            INSERT OR REPLACE INTO classifications
            (filename, description, country, keywords, confidence)
            VALUES (?, ?, ?, ?, ?)
            """, (
                result['filename'],
                result['description'],
                result['country'],
                json.dumps(result['keywords']),
                result['confidence']
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save result: {e}")
            return False

    def process_images(self):
        """Process all images in the directory"""
        # Find all images
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        all_images = []

        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if file.lower().endswith(image_extensions):
                    all_images.append(os.path.join(root, file))

        # Get already processed
        processed_images = self.get_processed_images()
        images_to_process = [img for img in all_images if os.path.basename(img) not in processed_images]

        print(f"\n{'='*60}")
        print(f"FAST MILITARY IMAGE CLASSIFIER")
        print(f"Total images found: {len(all_images)}")
        print(f"Already processed: {len(processed_images)}")
        print(f"Images to process: {len(images_to_process)}")
        print(f"{'='*60}")

        if not images_to_process:
            print("All images already processed!")
            self.show_results()
            return

        successful = 0
        failed = 0

        for i, image_path in enumerate(tqdm(images_to_process, desc="Classifying", unit="img"), 1):
            try:
                # Show progress every 20 images
                if i % 20 == 1:
                    filename = os.path.basename(image_path)
                    print(f"\n[PROGRESS] Processing {i}/{len(images_to_process)}: {filename[:40]}...")

                result = self.classify_image(image_path)
                self.save_result(result)

                if result['success']:
                    successful += 1

                    # Show sample results every 10 classifications
                    if successful % 10 == 0:
                        print(f"  [RESULT] {result['description'][:60]}...")
                        if result['country']:
                            print(f"    Country: {result['country']}")
                        if result['keywords']:
                            print(f"    Equipment: {', '.join(result['keywords'][:2])}")
                        print(".2f")

                else:
                    failed += 1

                # Memory management
                if self.device == "cuda" and i % 50 == 0:
                    torch.cuda.empty_cache()
                    gc.collect()

            except Exception as e:
                failed += 1
                print(f"[ERROR] Failed on {os.path.basename(image_path)}: {e}")

        print(f"\n{'='*60}")
        print(f"CLASSIFICATION COMPLETE!")
        print(f"Successfully classified: {successful}")
        print(f"Failed: {failed}")
        print(".1f")
        print(f"{'='*60}")

        self.show_results()

    def show_results(self):
        """Show summary of classification results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) FROM classifications")
        total = cursor.fetchone()[0]

        print(f"\nDATABASE SUMMARY: {total} images classified")
        print("-" * 40)

        # Country breakdown
        cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM classifications
        WHERE country IS NOT NULL
        GROUP BY country
        ORDER BY count DESC
        LIMIT 10
        """)

        print("\nTOP COUNTRIES DETECTED:")
        for country, count in cursor.fetchall():
            print(f"  {country}: {count} images")

        # Equipment breakdown
        cursor.execute("""
        SELECT json_extract(keywords, '$[0]') as top_keyword, COUNT(*) as count
        FROM classifications
        WHERE json_array_length(keywords) > 0
        GROUP BY top_keyword
        ORDER BY count DESC
        LIMIT 10
        """)

        print("\nTOP EQUIPMENT DETECTED:")
        for keyword, count in cursor.fetchall():
            if keyword:
                print(f"  {keyword}: {count} images")

        # Sample results
        cursor.execute("""
        SELECT filename, description, country, confidence
        FROM classifications
        WHERE confidence > 0.2
        ORDER BY confidence DESC
        LIMIT 5
        """)

        print("\nHIGHEST CONFIDENCE CLASSIFICATIONS:")
        for filename, desc, country, conf in cursor.fetchall():
            print(f"  {filename[:30]}... ({conf:.2f})")
            print(f"    {desc[:50]}...")
            if country:
                print(f"    Country: {country}")
            print()

        conn.close()

def main():
    print("Fast Military Image Classifier")
    print("Using CLIP for rapid classification (no detailed captions)")
    print("=" * 50)

    classifier = FastImageClassifier()
    classifier.process_images()

if __name__ == "__main__":
    main()
