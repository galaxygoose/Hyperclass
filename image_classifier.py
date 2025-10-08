import os
import torch
from PIL import Image, ExifTags
import psycopg2
from transformers import (
    Blip2Processor, Blip2ForConditionalGeneration,
    CLIPProcessor, CLIPModel
)
from tqdm import tqdm
import json
from datetime import datetime
import gc
import warnings
import re
from reverse_image_search import ReverseImageSearch
warnings.filterwarnings("ignore")

class ImageClassifier:
    def __init__(self, images_dir="images", db_params=None):
        self.images_dir = images_dir

        # Default database parameters - update these for your setup
        if db_params is None:
            self.db_params = {
                'host': 'localhost',
                'database': 'image_classification',
                'user': 'postgres',  # Update with your PostgreSQL username
                'password': 'password',  # Update with your PostgreSQL password
                'port': 5433
            }
        else:
            self.db_params = db_params

        # Initialize models
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Initialize BLIP-2 for image captioning
        print("Loading BLIP-2 model...")
        self.blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        self.blip_model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-2.7b",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)

        # Initialize CLIP for classification
        print("Loading CLIP model...")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Initialize reverse image search
        print("Initializing reverse image search...")
        self.reverse_search = ReverseImageSearch()

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

    def get_processed_images(self):
        """Get list of already processed image filenames"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("SELECT filename FROM image_metadata")
            processed = {row[0] for row in cursor.fetchall()}
            cursor.close()
            conn.close()
            return processed
        except Exception as e:
            print(f"Error getting processed images: {e}")
            return set()

    def save_to_database(self, filename, description, country, keywords, source_info=None, metadata_is_ai=False, exif_data=None):
        """Save image metadata to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Prepare source info
            source_url = source_info.get('source_url', '') if source_info else ''
            source_type = source_info.get('source_type', '') if source_info else ''
            original_title = source_info.get('original_title', '') if source_info else ''
            filename_originator = source_info.get('filename_originator', '') if source_info else ''
            image_url = source_info.get('image_url', '') if source_info else ''

            # Prepare EXIF data
            exif_camera_make = exif_data.get('camera_make', '') if exif_data else ''
            exif_camera_model = exif_data.get('camera_model', '') if exif_data else ''
            exif_datetime_original = exif_data.get('datetime_original', '') if exif_data else ''
            exif_gps_latitude = exif_data.get('gps_latitude', '') if exif_data else ''
            exif_gps_longitude = exif_data.get('gps_longitude', '') if exif_data else ''
            exif_software = exif_data.get('software', '') if exif_data else ''
            exif_copyright = exif_data.get('copyright', '') if exif_data else ''

            # Insert or update the record
            query = """
            INSERT INTO image_metadata (filename, description, country, keywords, source_url, source_type, original_title, metadata_is_ai, filename_originator, image_url, exif_camera_make, exif_camera_model, exif_datetime_original, exif_gps_latitude, exif_gps_longitude, exif_software, exif_copyright)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (filename) DO UPDATE SET
                description = EXCLUDED.description,
                country = EXCLUDED.country,
                keywords = EXCLUDED.keywords,
                source_url = EXCLUDED.source_url,
                source_type = EXCLUDED.source_type,
                original_title = EXCLUDED.original_title,
                metadata_is_ai = EXCLUDED.metadata_is_ai,
                filename_originator = EXCLUDED.filename_originator,
                image_url = EXCLUDED.image_url,
                exif_camera_make = EXCLUDED.exif_camera_make,
                exif_camera_model = EXCLUDED.exif_camera_model,
                exif_datetime_original = EXCLUDED.exif_datetime_original,
                exif_gps_latitude = EXCLUDED.exif_gps_latitude,
                exif_gps_longitude = EXCLUDED.exif_gps_longitude,
                exif_software = EXCLUDED.exif_software,
                exif_copyright = EXCLUDED.exif_copyright,
                processed_at = CURRENT_TIMESTAMP
            """

            cursor.execute(query, (filename, description, country, keywords, source_url, source_type, original_title, metadata_is_ai, filename_originator, image_url, exif_camera_make, exif_camera_model, exif_datetime_original, exif_gps_latitude, exif_gps_longitude, exif_software, exif_copyright))
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
            batch_size = 8  # Reduced batch size to avoid sequence length issues

            # Truncate keyword texts to avoid sequence length issues
            keyword_texts = [text[:150] for text in keyword_texts]  # Limit text length

            for i in range(0, len(keyword_texts), batch_size):
                batch_texts = keyword_texts[i:i+batch_size]

                try:
                    inputs = self.clip_processor(text=batch_texts, images=image, return_tensors="pt", padding=True, truncation=True, max_length=77)
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

                except Exception as e:
                    print(f"Error in keyword batch {i//batch_size}: {e}")
                    continue

            return keywords_found[:10]  # Limit to top 10 keywords
        except Exception as e:
            print(f"Error extracting keywords for {image_path}: {e}")
            return []

    def _select_best_reverse_result(self, results):
        """Select the best reverse image search result based on quality criteria"""
        if not results:
            return None

        # Prioritize AFP and Shutterstock results
        afp_shutterstock = [r for r in results if any(domain in r.get('url', '').lower()
                                                      for domain in ['afp.com', 'shutterstock.com', 'gettyimages.com'])]

        if afp_shutterstock:
            # Return the one with the most descriptive information
            return max(afp_shutterstock, key=lambda x: len(x.get('description', '')) + len(x.get('title', '')))

        # Fallback to any result with good description
        descriptive_results = [r for r in results if len(r.get('description', '')) > 20]
        if descriptive_results:
            return descriptive_results[0]

        # Return first result as fallback
        return results[0]

    def _create_realistic_description(self, metadata):
        """Create a realistic AFP-style description from metadata"""
        description_parts = []

        # Start with the main description
        if metadata.get('description'):
            desc = metadata['description'].strip()
            # Clean up the description to sound more like AFP
            desc = re.sub(r'\s+', ' ', desc)  # Normalize whitespace
            desc = re.sub(r'^[A-Z\s]+:', '', desc)  # Remove location prefixes if present
            description_parts.append(desc)

        # Add location if available
        if metadata.get('location'):
            location = metadata['location'].strip()
            if location and location not in description_parts[0] if description_parts else True:
                description_parts.insert(0, f"In {location}")

        # Add date context if available
        if metadata.get('date'):
            date_str = metadata['date'].strip()
            if date_str:
                description_parts.append(f"({date_str})")

        # Add source attribution
        source = metadata.get('source', '')
        if source:
            description_parts.append(f"Source: {source}")

        final_description = '. '.join(description_parts)

        # Ensure it sounds like a professional news description
        if not final_description:
            return "Military equipment photographed during operations"

        # Capitalize first letter
        if final_description:
            final_description = final_description[0].upper() + final_description[1:]

        return final_description

    def _extract_country_from_metadata(self, metadata):
        """Extract country information from metadata"""
        # Check keywords for country names
        keywords = metadata.get('keywords', [])
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for country in self.country_categories:
                if country.lower() in keyword_lower:
                    return country

        # Check description for country mentions
        description = metadata.get('description', '').lower()
        for country in self.country_categories:
            if country.lower() in description:
                return country

        # Check URL for country hints
        url = metadata.get('url', '').lower()
        country_hints = {
            'iran': 'Iran',
            'russia': 'Russia',
            'china': 'China',
            'northkorea': 'North Korea',
            'israel': 'Israel',
            'ukraine': 'Ukraine',
            'usa': 'United States',
            'us': 'United States'
        }

        for hint, country in country_hints.items():
            if hint in url:
                return country

        return None

    def _enhance_ai_description(self, ai_description):
        """Enhance AI-generated description to be more realistic and descriptive, but not always military"""
        if not ai_description:
            return "Equipment photographed in operational setting"

        # Remove generic AI prefixes
        ai_description = re.sub(r'^(a photo of|a picture of|an image of|this is|here is)\s+', '', ai_description, flags=re.IGNORECASE)

        # Check if this appears to be military equipment
        military_indicators = [
            'missile', 'tank', 'armored vehicle', 'fighter jet', 'military aircraft',
            'warship', 'submarine', 'soldier', 'military uniform', 'radar',
            'anti-aircraft', 'sam', 'surface-to-air missile', 'nuclear weapon'
        ]

        is_military = any(indicator in ai_description.lower() for indicator in military_indicators)

        # Only enhance military terms if it appears to be military equipment
        if is_military:
            enhancements = {
                'military equipment': 'military hardware',
                'soldiers': 'military personnel',
                'tank': 'armored vehicle',
                'helicopter': 'military helicopter',
                'aircraft': 'military aircraft',
                'missile': 'ballistic missile system',
                'launcher': 'missile launcher'
            }

            enhanced = ai_description
            for generic, specific in enhancements.items():
                enhanced = re.sub(r'\b' + re.escape(generic) + r'\b', specific, enhanced, flags=re.IGNORECASE)

            # Add professional context for military
            if not any(word in enhanced.lower() for word in ['photographed', 'shown', 'displayed', 'during', 'operations', 'exercise', 'maneuver']):
                # Be more specific about the context
                if 'parade' in enhanced.lower() or 'ceremony' in enhanced.lower():
                    enhanced += " during military parade"
                elif 'training' in enhanced.lower():
                    enhanced += " during military training"
                else:
                    enhanced += " in military setting"
        else:
            # For non-military images, keep more neutral
            enhanced = ai_description
            # Still add some professional context
            if not any(word in enhanced.lower() for word in ['photographed', 'shown', 'displayed', 'during', 'operations']):
                enhanced += " photographed in operational setting"

        # Capitalize properly
        enhanced = enhanced[0].upper() + enhanced[1:] if enhanced else enhanced

        return enhanced

    def extract_exif_data(self, image_path):
        """
        Extract EXIF metadata from image file
        Returns a dict with EXIF data or empty dict if no EXIF
        """
        exif_data = {
            'camera_make': '',
            'camera_model': '',
            'datetime_original': '',
            'gps_latitude': '',
            'gps_longitude': '',
            'image_width': '',
            'image_height': '',
            'software': '',
            'copyright': ''
        }

        try:
            image = Image.open(image_path)
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif_dict = image._getexif()

                # Map EXIF tags to readable names
                exif_mapping = {
                    'Make': 'camera_make',
                    'Model': 'camera_model',
                    'DateTimeOriginal': 'datetime_original',
                    'Software': 'software',
                    'Copyright': 'copyright',
                    'ExifImageWidth': 'image_width',
                    'ExifImageHeight': 'image_height'
                }

                for tag, value in exif_dict.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    if tag_name in exif_mapping:
                        exif_data[exif_mapping[tag_name]] = str(value)

                # Extract GPS data if available
                if 'GPSInfo' in exif_dict:
                    gps_info = exif_dict['GPSInfo']
                    if gps_info:
                        # GPS latitude
                        if 2 in gps_info and 4 in gps_info:
                            lat = self._convert_gps_coordinates(gps_info[2], gps_info[1])
                            exif_data['gps_latitude'] = lat

                        # GPS longitude
                        if 4 in gps_info and 6 in gps_info:
                            lon = self._convert_gps_coordinates(gps_info[4], gps_info[3])
                            exif_data['gps_longitude'] = lon

        except Exception as e:
            print(f"Error extracting EXIF data from {image_path}: {e}")

        return exif_data

    def _convert_gps_coordinates(self, coordinates, ref):
        """
        Convert GPS coordinates from EXIF format to decimal degrees
        """
        try:
            degrees = float(coordinates[0])
            minutes = float(coordinates[1])
            seconds = float(coordinates[2])

            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

            if ref in ['S', 'W']:
                decimal = -decimal

            return f"{decimal:.6f}"
        except:
            return ""

    def process_image(self, image_path):
        """Process a single image and extract all metadata"""
        filename = os.path.basename(image_path)

        # Extract EXIF data first (this is always real data when available)
        exif_data = self.extract_exif_data(image_path)
        has_exif = any(exif_data.values())  # Check if any EXIF data was found
        if has_exif:
            print(f"Found EXIF data: {sum(1 for v in exif_data.values() if v)} fields")

        # Generate AI description first (needed for search query)
        ai_description = self.generate_caption(image_path)
        ai_description = self._enhance_ai_description(ai_description)

        # Try reverse image search using the AI description as search query
        print(f"Performing reverse image search for {filename}...")
        reverse_results = self.reverse_search.search_and_extract_metadata(image_path, ai_description, max_results=3)

        description = None
        country = None
        keywords = []
        source_info = {}

        metadata_is_ai = False  # Default to real metadata

        # Process reverse image search results
        if reverse_results:
            print(f"Found {len(reverse_results)} reverse image search results")
            best_result = self._select_best_reverse_result(reverse_results)

            if best_result:
                description = self._create_realistic_description(best_result)
                country = self._extract_country_from_metadata(best_result)
                keywords = best_result.get('keywords', [])
                source_info = {
                    'source_url': best_result.get('url', ''),
                    'source_type': best_result.get('source', ''),
                    'original_title': best_result.get('title', ''),
                    'filename_originator': best_result.get('filename_originator', ''),
                    'image_url': best_result.get('image_url', '')
                }
                metadata_is_ai = False  # Real metadata from search
                print(f"Using metadata from {best_result.get('source', 'unknown source')}")
            else:
                # Use AI description if reverse search didn't find good results
                description = ai_description
                metadata_is_ai = True
                print("Reverse search found results but none were suitable, using AI description")
        else:
            print("No reverse image search results found, using AI classification")
            description = ai_description
            metadata_is_ai = True  # AI-generated

        if not country:
            country = self.classify_country(image_path)

        if not keywords:
            keywords = self.extract_keywords(image_path, description)

        # Save to database with EXIF data
        success = self.save_to_database(filename, description, country, keywords, source_info, metadata_is_ai, exif_data)

        return {
            'filename': filename,
            'description': description,
            'country': country,
            'keywords': keywords,
            'source_info': source_info,
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

        for image_path in tqdm(images_to_process, desc="Processing images"):
            try:
                result = self.process_image(image_path)
                if result['success']:
                    successful += 1
                else:
                    failed += 1

                # Clear GPU cache periodically
                if torch.cuda.is_available() and successful % 10 == 0:
                    torch.cuda.empty_cache()
                    gc.collect()

            except Exception as e:
                print(f"Failed to process {image_path}: {e}")
                failed += 1

        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful}")
        print(f"Failed: {failed}")

def main():
    # Initialize classifier
    classifier = ImageClassifier()

    # Process all images
    classifier.process_all_images()

if __name__ == "__main__":
    main()
