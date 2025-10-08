import os
import torch
from PIL import Image
import sqlite3
from transformers import (
    Blip2Processor, Blip2ForConditionalGeneration,
    CLIPProcessor, CLIPModel
)
from tqdm import tqdm
import json
from datetime import datetime
import gc
import warnings
warnings.filterwarnings("ignore")

class ImageClassifierSQLite:
    def __init__(self, images_dir="images", db_path="image_classification.db"):
        self.images_dir = images_dir
        self.db_path = db_path

        # Initialize models
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Initialize BLIP-2 for image captioning
        print("Loading BLIP-2 model... (this may take several minutes)")
        print("Progress: Downloading model files...")
        self.blip_processor = Blip2Processor.from_pretrained(
            "Salesforce/blip2-opt-2.7b",
            resume_download=True,
            force_download=False
        )
        print("Progress: Loading BLIP-2 model weights...")
        self.blip_model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-2.7b",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            resume_download=True,
            force_download=False,
            device_map="auto" if self.device == "cuda" else None
        ).to(self.device)
        print("✓ BLIP-2 model loaded successfully!")

        # Initialize CLIP for classification
        print("Loading CLIP model... (smaller, faster download)")
        self.clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            resume_download=True,
            force_download=False
        ).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            resume_download=True,
            force_download=False
        )
        print("✓ CLIP model loaded successfully!")

        # Define classification categories
        self.country_categories = [
            "United States", "Russia", "China", "North Korea", "Iran", "Israel",
            "Ukraine", "United Kingdom", "France", "Germany", "Japan", "India",
            "Syria", "Iraq", "Afghanistan", "Pakistan", "Turkey", "Saudi Arabia",
            "Egypt", "Lebanon", "Gaza Strip", "Taiwan", "South Korea", "Vietnam",
            "Cuba", "Venezuela", "Brazil", "Mexico", "Canada", "Australia"
        ]

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

        # Setup SQLite database
        self.setup_database()

    def setup_database(self):
        """Set up SQLite database and table for image classification data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for image metadata
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            description TEXT,
            country TEXT,
            keywords TEXT,  -- JSON array of keywords
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'processed'
        );
        """)

        # Create index on filename for faster lookups
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_filename ON image_metadata(filename);
        """)

        conn.commit()
        conn.close()
        print("SQLite database setup complete!")

    def get_processed_images(self):
        """Get list of already processed image filenames"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM image_metadata")
            processed = {row[0] for row in cursor.fetchall()}
            cursor.close()
            conn.close()
            return processed
        except Exception as e:
            print(f"Error getting processed images: {e}")
            return set()

    def save_to_database(self, filename, description, country, keywords):
        """Save image metadata to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert keywords list to JSON string
            keywords_json = json.dumps(keywords) if keywords else None

            # Insert or update the record
            cursor.execute("""
            INSERT OR REPLACE INTO image_metadata (filename, description, country, keywords)
            VALUES (?, ?, ?, ?)
            """, (filename, description, country, keywords_json))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False

    def generate_caption(self, image_path):
        """Generate detailed caption for the image using BLIP-2"""
        try:
            image = Image.open(image_path).convert('RGB')

            # Generate caption
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device, torch.float16 if self.device == "cuda" else torch.float32)
            generated_ids = self.blip_model.generate(**inputs, max_new_tokens=50)
            caption = self.blip_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

            return caption
        except Exception as e:
            print(f"Error generating caption for {image_path}: {e}")
            return "Unable to generate caption"

    def classify_country(self, image_path):
        """Classify country based on flags, uniforms, or equipment"""
        try:
            image = Image.open(image_path).convert('RGB')

            # Prepare text inputs for country classification
            texts = [f"flag of {country}" for country in self.country_categories] + \
                   [f"military equipment from {country}" for country in self.country_categories] + \
                   [f"uniform of {country} military" for country in self.country_categories]

            inputs = self.clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Get top predictions
            top_probs, top_indices = torch.topk(probs[0], 3)

            detected_countries = []
            for prob, idx in zip(top_probs, top_indices):
                if prob > 0.1:  # Confidence threshold
                    country_text = texts[idx]
                    # Extract country name from text
                    for country in self.country_categories:
                        if country in country_text:
                            detected_countries.append(country)
                            break

            return detected_countries[0] if detected_countries else None
        except Exception as e:
            print(f"Error classifying country for {image_path}: {e}")
            return None

    def extract_keywords(self, image_path, caption):
        """Extract relevant keywords using CLIP classification"""
        try:
            image = Image.open(image_path).convert('RGB')

            # Use caption + keyword combinations for better context
            keyword_texts = [f"{caption} with {keyword}" for keyword in self.military_keywords[:50]]  # Limit for memory
            keyword_texts.extend(self.military_keywords[:50])  # Also test keywords alone

            # Process in batches to avoid memory issues
            keywords_found = []
            batch_size = 16

            for i in range(0, len(keyword_texts), batch_size):
                batch_texts = keyword_texts[i:i+batch_size]

                inputs = self.clip_processor(text=batch_texts, images=image, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.clip_model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = logits_per_image.softmax(dim=1)

                # Find keywords with high confidence
                for j, prob in enumerate(probs[0]):
                    if prob > 0.15:  # Confidence threshold
                        keyword_text = batch_texts[j]
                        # Extract the keyword part
                        for keyword in self.military_keywords:
                            if keyword in keyword_text:
                                if keyword not in keywords_found:
                                    keywords_found.append(keyword)
                                break

            return keywords_found[:10]  # Limit to top 10 keywords
        except Exception as e:
            print(f"Error extracting keywords for {image_path}: {e}")
            return []

    def process_image(self, image_path):
        """Process a single image and extract all metadata"""
        filename = os.path.basename(image_path)

        # Generate caption
        description = self.generate_caption(image_path)

        # Classify country
        country = self.classify_country(image_path)

        # Extract keywords
        keywords = self.extract_keywords(image_path, description)

        # Save to database
        success = self.save_to_database(filename, description, country, keywords)

        return {
            'filename': filename,
            'description': description,
            'country': country,
            'keywords': keywords,
            'success': success
        }

    def process_all_images(self):
        """Process all images in the images directory"""
        # Get list of image files
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        image_files = []

        for root, dirs, files in os.walk(self.images_dir):
            for file in files:
                if file.lower().endswith(image_extensions):
                    image_files.append(os.path.join(root, file))

        print(f"Found {len(image_files)} images to process")

        # Get already processed images
        processed_images = self.get_processed_images()
        print(f"Already processed {len(processed_images)} images")

        # Filter out already processed images
        images_to_process = [img for img in image_files if os.path.basename(img) not in processed_images]

        print(f"Processing {len(images_to_process)} new images")

        # Process images with progress bar
        successful = 0
        failed = 0

        print(f"\n{'='*60}")
        print(f"STARTING IMAGE CLASSIFICATION")
        print(f"Total images to process: {len(images_to_process)}")
        print(f"Using device: {self.device}")
        print(f"{'='*60}")

        for i, image_path in enumerate(tqdm(images_to_process, desc="Processing images", unit="img"), 1):
            try:
                filename = os.path.basename(image_path)

                # Show progress every 50 images
                if i % 50 == 0 or i == 1:
                    print(f"\n[PROGRESS] Processing image {i}/{len(images_to_process)}: {filename[:50]}...")

                result = self.process_image(image_path)
                if result['success']:
                    successful += 1

                    # Show sample results every 10 successful classifications
                    if successful % 10 == 0:
                        print(f"  [OK] Classified: {result['description'][:80]}...")
                        if result['country']:
                            print(f"    Country: {result['country']}")
                        if result['keywords']:
                            print(f"    Keywords: {', '.join(result['keywords'][:3])}")

                else:
                    failed += 1

                # Clear GPU cache periodically
                if torch.cuda.is_available() and i % 25 == 0:
                    print("  [SYSTEM] Clearing GPU cache...")
                    torch.cuda.empty_cache()
                    gc.collect()

            except Exception as e:
                print(f"[ERROR] Failed to process {os.path.basename(image_path)}: {e}")
                failed += 1

        print(f"\n{'='*60}")
        print(f"CLASSIFICATION COMPLETE!")
        print(f"Successfully processed: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful/(successful+failed)*100):.1f}%" if (successful+failed) > 0 else "N/A")
        print(f"{'='*60}")

def main():
    # Initialize classifier
    classifier = ImageClassifierSQLite()

    # Process all images
    classifier.process_all_images()

if __name__ == "__main__":
    main()
