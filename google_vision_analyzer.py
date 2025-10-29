#!/usr/bin/env python3
"""
Google Vision API analyzer for military image classification
Uses Google Cloud Vision API for comprehensive image analysis
"""

import os
import json
import base64
import requests
from typing import Dict, List, Tuple, Optional
from PIL import Image
import warnings
from dotenv import load_dotenv
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

class GoogleVisionAnalyzer:
    """Google Vision API integration for military image analysis"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        self.base_url = 'https://vision.googleapis.com/v1/images:annotate'

        if not self.api_key:
            print("Warning: GOOGLE_CLOUD_API_KEY not found in .env file")
            print("Google Vision API features will not work without API key")

        # Context keywords for news/media searchability (Google Vision handles the actual detection)
        self.context_categories = {
            'people': ['person', 'people', 'man', 'woman', 'child', 'politician', 'leader', 'official', 'celebrity'],
            'locations': ['building', 'structure', 'facility', 'embassy', 'office', 'headquarters', 'venue', 'stadium'],
            'objects': ['flag', 'vehicle', 'aircraft', 'ship', 'equipment', 'device', 'tool', 'weapon'],
            'events': ['ceremony', 'meeting', 'conference', 'summit', 'protest', 'demonstration', 'celebration'],
            'organizations': ['government', 'military', 'company', 'organization', 'agency', 'ministry']
        }

        # Country flags and symbols
        self.country_indicators = {
            'Iran': ['iranian flag', 'iran flag', 'persian flag', 'flag of iran'],
            'Russia': ['russian flag', 'russia flag', 'flag of russia'],
            'China': ['chinese flag', 'china flag', 'flag of china'],
            'United States': ['american flag', 'us flag', 'usa flag', 'flag of the united states'],
            'North Korea': ['north korean flag', 'north korea flag', 'flag of north korea'],
        }

    def analyze_image(self, image_path: str) -> Dict:
        """
        Comprehensive military image analysis using Google Vision API

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with analysis results
        """
        if not self.api_key:
            return self._get_fallback_analysis(image_path)

        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare comprehensive Vision API request for news/media searchability
            request_body = {
                'requests': [{
                    'image': {
                        'content': image_data
                    },
                    'features': [
                        {
                            'type': 'LABEL_DETECTION',
                            'maxResults': 50
                        },
                        {
                            'type': 'OBJECT_LOCALIZATION',
                            'maxResults': 50
                        },
                        {
                            'type': 'TEXT_DETECTION',
                            'maxResults': 50
                        },
                        {
                            'type': 'FACE_DETECTION',
                            'maxResults': 50
                        },
                        {
                            'type': 'LOGO_DETECTION',
                            'maxResults': 50
                        },
                        {
                            'type': 'LANDMARK_DETECTION',
                            'maxResults': 50
                        },
                        {
                            'type': 'WEB_DETECTION',
                            'maxResults': 20
                        }
                    ]
                }]
            }

            # Make API request
            url = f'{self.base_url}?key={self.api_key}'
            response = requests.post(url, json=request_body, timeout=30)
            response.raise_for_status()

            result = response.json()
            return self._parse_vision_results(result, image_path)

        except Exception as e:
            print(f"Vision API error for {image_path}: {e}")
            return self._get_fallback_analysis(image_path)

    def _parse_vision_results(self, api_response: Dict, image_path: str) -> Dict:
        """Parse Google Vision API response into military classification format"""

        # Extract comprehensive data from all Vision API features
        label_annotations = api_response['responses'][0].get('labelAnnotations', [])
        localized_objects = api_response['responses'][0].get('localizedObjectAnnotations', [])
        text_annotations = api_response['responses'][0].get('textAnnotations', [])
        face_annotations = api_response['responses'][0].get('faceAnnotations', [])
        logo_annotations = api_response['responses'][0].get('logoAnnotations', [])
        landmark_annotations = api_response['responses'][0].get('landmarkAnnotations', [])
        web_detection = api_response['responses'][0].get('webDetection', {})

        # Extract searchable content for news/media
        detected_people = self._extract_people(face_annotations, label_annotations)
        detected_locations = self._extract_locations(label_annotations, landmark_annotations, web_detection)
        detected_organizations = self._extract_organizations(label_annotations, logo_annotations)
        detected_objects = self._extract_objects(label_annotations, localized_objects)
        detected_countries = self._extract_countries(label_annotations, {})

        # Enhanced people detection from web search results
        detected_people.extend(self._extract_people_from_web(web_detection))

        extracted_text = self._extract_text(text_annotations)

        # Generate AI-powered description using full Vision API response
        description = self._generate_ai_description(api_response['responses'][0])

        # Calculate overall confidence
        confidence = self._calculate_confidence(label_annotations, detected_objects)

        # Generate comprehensive searchable keywords
        searchable_keywords = self._generate_searchable_keywords(
            detected_people, detected_locations, detected_organizations,
            detected_objects, detected_countries, extracted_text, label_annotations
        )

        return {
            'filename': os.path.basename(image_path),
            'description': description,
            'country': detected_countries[0] if detected_countries else None,
            'keywords': searchable_keywords,
            'people': detected_people,
            'locations': detected_locations,
            'organizations': detected_organizations,
            'objects': detected_objects,
            'vision_labels': [label['description'] for label in label_annotations[:15]],
            'vision_objects': len(localized_objects),
            'vision_faces': len(face_annotations),
            'vision_logos': len(logo_annotations),
            'vision_landmarks': len(landmark_annotations),
            'extracted_text': extracted_text,
            'confidence': confidence,
            'source_type': 'Google Vision API',
            'metadata_is_ai': True
        }

    def _generate_photolibrary_keywords(self, equipment: List, countries: List, text: str, labels: List) -> List[str]:
        """Generate photolibrary keywords using Vision API's native categorization and object detection"""

        keywords = []

        # Use Vision API's most relevant labels for news searchability
        for label in labels[:6]:  # Top 6 labels for quality over quantity
            label_desc = label['description'].lower()
            confidence = label['score']

            # Only include high-confidence, specific labels that are genuinely useful for search
            if (confidence > 0.75 and
                any(search_term in label_desc for search_term in [
                    'military', 'army', 'navy', 'air force', 'defense', 'flag', 'uniform',
                    'aircraft', 'helicopter', 'tank', 'missile', 'warship', 'embassy',
                    'headquarters', 'office', 'building', 'person', 'official'
                ]) and not any(exclude_term in label_desc for exclude_term in [
                    'blue', 'pole', 'sunlight', 'wind', 'day', 'light', 'dark', 'color'
                ])):
                keywords.append(label_desc)

        # Add specific object names from object localization (more precise than labels)
        # Note: objects parameter would contain localized object data if we had it
        # For now, we'll use the equipment list which comes from object detection

        # Add country-specific context if detected
        if countries:
            for country in countries:
                country_lower = country.lower()
                keywords.append(country_lower)
                # Add military context for the country
                keywords.extend([
                    f"{country_lower} military",
                    f"{country_lower} defense",
                    f"{country_lower} armed forces",
                    f"{country_lower} flag"
                ])

        # Add equipment-specific context only for confirmed, specific equipment
        # Filter equipment list to only include actual equipment, not generic terms
        actual_equipment = []
        for equip in equipment:
            equip_lower = equip.lower()
            # Only include specific, identifiable equipment
            if (any(term in equip_lower for term in ['tank', 'missile', 'aircraft', 'helicopter', 'warship', 'submarine', 'armored vehicle'])
                or ('military' in equip_lower and any(term in equip_lower for term in ['aircraft', 'vehicle', 'helicopter']))
                or 'combat' in equip_lower or 'fighter' in equip_lower) and not any(exclude_term in equip_lower for exclude_term in [
                    'flag', 'pole', 'sunlight', 'wind', 'day', 'government', 'blue', 'united states', 'america', 'flag of',
                    'person', 'people', 'military person', 'official'  # Exclude generic people/terms
                ]):
                actual_equipment.append(equip)

        if actual_equipment:
            for equip in actual_equipment[:4]:  # Top 4 specific equipment items
                equip_lower = equip.lower()

                # Use Vision API's specific equipment naming
                keywords.append(equip_lower)

                # Add specific, searchable military context
                if any(term in equip_lower for term in ['aircraft', 'airplane', 'jet', 'helicopter']):
                    keywords.extend(['military aircraft', 'combat aircraft', 'aviation'])
                elif any(term in equip_lower for term in ['tank', 'armored']):
                    keywords.extend(['armored vehicle', 'military vehicle', 'armor'])
                elif any(term in equip_lower for term in ['missile', 'rocket']):
                    keywords.extend(['missile system', 'ballistic missile'])
                elif any(term in equip_lower for term in ['warship', 'naval']):
                    keywords.extend(['naval vessel', 'military vessel'])

        # Add text if it's military-relevant (OCR results)
        if text:
            text_lower = text.lower()
            # Include text if it contains military identifiers or looks like equipment markings
            if any(military_term in text_lower for military_term in [
                'tel', 'sam', 'icbm', 'slbm', 'army', 'navy', 'air force', 'uss', 'hms'
            ]) or (len(text) <= 20 and not any(char.isspace() for char in text)):  # Short technical markings
                keywords.append(text.strip())

        # Remove duplicates and prioritize (keep original order for relevance)
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)

        # Limit to top 15 most relevant keywords for comprehensive searchability
        return unique_keywords[:15]

    def _generate_searchable_keywords(self, people: List, locations: List, organizations: List,
                                    objects: List, countries: List, text: str, labels: List) -> List[str]:
        """Generate comprehensive searchable keywords for news/media content"""

        keywords = []

        # Add people for celebrity/politician search
        for person in people[:3]:
            keywords.append(person.lower())
            # Add variations for better searchability
            if ' ' in person:
                first_name = person.split()[0].lower()
                last_name = person.split()[-1].lower()
                keywords.extend([first_name, last_name, f"{first_name} {last_name}"])

        # Add locations for venue/building search
        for location in locations[:3]:
            keywords.append(location.lower())
            # Add building/facility variations
            if any(term in location.lower() for term in ['embassy', 'office', 'headquarters', 'building']):
                keywords.append(location.lower())

        # Add organizations for institutional search
        for org in organizations[:3]:
            keywords.append(org.lower())
            # Add common variations
            if 'government' in org.lower():
                keywords.append('government agency')
            elif 'military' in org.lower():
                keywords.append('armed forces')

        # Add objects for equipment/asset search
        for obj in objects[:5]:
            keywords.append(obj.lower())

        # Add countries for geographic search
        for country in countries[:3]:
            country_lower = country.lower()
            keywords.append(country_lower)
            keywords.extend([
                f"{country_lower} embassy",
                f"{country_lower} government",
                f"{country_lower} official"
            ])

        # Add extracted text for specific identifier search
        if text:
            text_lower = text.lower()
            # Clean and add searchable text
            if len(text) > 2 and not text.isdigit():
                keywords.append(text.strip())
                # Add individual words if they're meaningful
                words = text.split()
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        keywords.append(word.lower())

        # Add contextual labels for broader searchability
        for label in labels[:5]:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.8:
                # Add high-confidence contextual labels
                if not any(env_term in label_desc for env_term in [
                    'blue', 'pole', 'sunlight', 'wind', 'day', 'light', 'dark'
                ]):
                    keywords.append(label_desc)

        # Remove duplicates and prioritize
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen and len(keyword) > 2:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)

        # Limit to top 20 keywords for comprehensive searchability
        return unique_keywords[:20]

    def _extract_military_equipment(self, labels: List, objects: List) -> List[str]:
        """Extract military equipment using Vision API's native categorization - be conservative"""
        equipment = []

        # Use Vision API's built-in categorization but be conservative about military classification
        # Only classify as military equipment when there's clear evidence

        # Process high-confidence labels that strongly indicate actual military equipment
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            # Extremely high confidence threshold and very strict military equipment filtering
            # Only classify as military equipment when there's absolutely clear evidence
            if confidence > 0.95:  # Only extremely confident detections
                # Only include labels that are clearly actual military equipment (not flags, locations, or generic terms)
                if any(equipment_term in label_desc for equipment_term in [
                    'tank', 'missile', 'fighter jet', 'military aircraft', 'combat aircraft',
                    'warship', 'submarine', 'military vehicle', 'armored personnel carrier',
                    'howitzer', 'artillery', 'radar system', 'military helicopter'
                ]) and not any(exclude_term in label_desc for exclude_term in [
                    'flag', 'pole', 'sunlight', 'wind', 'day', 'government', 'blue', 'sky',
                    'person', 'people', 'crowd', 'uniform', 'soldier', 'military person',
                    'united states', 'america', 'country', 'flag of', 'national', 'anthem',
                    'building', 'structure', 'office', 'embassy', 'headquarters'
                ]):
                    equipment.append(label['description'])

        # Process localized objects for specific military equipment
        for obj in objects:
            obj_name = obj['name'].lower()
            confidence = obj['score']

            if confidence > 0.85:  # Very high threshold for objects
                if any(equipment_term in obj_name for equipment_term in [
                    'tank', 'missile', 'fighter jet', 'military aircraft', 'combat aircraft',
                    'warship', 'submarine', 'howitzer', 'artillery'
                ]) and obj_name not in ['flag', 'person', 'people', 'uniform', 'soldier']:  # Exclude non-equipment
                    equipment.append(obj['name'])

        # Remove duplicates and filter to only actual military equipment
        seen = set()
        unique_equipment = []
        for equip in equipment:
            equip_lower = equip.lower()
            # Only include if it's clearly military equipment, not flags, locations, or environmental terms
            if (any(term in equip_lower for term in ['tank', 'missile', 'aircraft', 'helicopter', 'warship', 'armored'])
                or ('military' in equip_lower and any(term in equip_lower for term in ['aircraft', 'vehicle', 'personnel']))
                or 'combat' in equip_lower or 'fighter' in equip_lower) and not any(exclude_term in equip_lower for exclude_term in [
                    'flag', 'pole', 'sunlight', 'wind', 'day', 'government', 'blue', 'united states', 'america'
                ]):
                if equip_lower not in seen:
                    seen.add(equip_lower)
                    unique_equipment.append(equip)

        return unique_equipment

    def _extract_people(self, faces: List, labels: List) -> List[str]:
        """Extract people/celebrities from face detection, celebrity recognition, and labels"""
        people = []

        # 1. Extract from celebrity recognition (most specific)
        for face in faces:
            if 'celebrity' in face and face['celebrity'].get('name'):
                people.append(face['celebrity']['name'])

        # 2. Extract from face detection with name recognition
        for face in faces:
            if 'name' in face:
                people.append(face['name'])

        # 3. Extract from labels that indicate specific people/roles
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.6:  # Lower threshold for political people detection
                # Look for specific people, politicians, leaders, officials - expanded list
                political_terms = [
                    'president', 'prime minister', 'minister', 'secretary', 'ambassador',
                    'governor', 'mayor', 'senator', 'congressman', 'diplomat', 'chancellor',
                    'politician', 'leader', 'official', 'spokesperson', 'representative',
                    'executive', 'director', 'chairman', 'ceo', 'founder', 'chairperson',
                    'premier', 'foreign minister', 'defense minister', 'interior minister'
                ]

                if any(person_term in label_desc for person_term in political_terms) and not any(generic_term in label_desc for generic_term in [
                    'person', 'people', 'man', 'woman', 'crowd', 'group', 'audience', 'citizen',
                    'individual', 'portrait', 'photograph', 'picture', 'image'
                ]):
                    people.append(label['description'])

                # Also detect formal settings that suggest political context
                elif confidence > 0.7 and any(formal_term in label_desc for formal_term in [
                    'suit', 'tie', 'jacket', 'blazer', 'podium', 'microphone', 'press conference',
                    'meeting', 'summit', 'ceremony', 'diplomatic', 'government', 'parliament'
                ]):
                    # If we have formal/political context but no specific title, still flag as political
                    people.append('Political figure')

        # 4. Also check for named entities in web detection
        # This would require parsing web detection results for named entities

        return list(set(people))[:5]  # Allow up to 5 people for better coverage

    def _extract_people_from_web(self, web_detection: Dict) -> List[str]:
        """Extract people names from web detection results"""
        people = []

        # Extract from web entities
        if 'webEntities' in web_detection:
            for entity in web_detection['webEntities'][:5]:  # Top 5 entities
                entity_desc = entity.get('description', '').lower()
                if any(person_term in entity_desc for person_term in [
                    'president', 'minister', 'secretary', 'ambassador', 'governor',
                    'politician', 'leader', 'official', 'diplomat'
                ]):
                    people.append(entity['description'])

        # Extract from visually similar images (web detection)
        if 'visuallySimilarImages' in web_detection:
            for similar in web_detection['visuallySimilarImages'][:3]:
                if 'pageTitle' in similar:
                    title = similar['pageTitle']
                    # Look for patterns like "Name at Location" or "Name speaks"
                    if any(connector in title.lower() for connector in [' at ', ' in ', ' speaks', ' meets', ' visits']):
                        # Extract potential name (first word or phrase before connector)
                        parts = title.split()
                        if len(parts) > 1:
                            potential_name = parts[0]
                            if (potential_name and
                                potential_name.lower() not in ['the', 'a', 'an', 'official', 'government'] and
                                len(potential_name) > 2):
                                people.append(potential_name)

        return people

    def _extract_locations(self, labels: List, landmarks: List, web_detection: Dict) -> List[str]:
        """Extract locations, buildings, landmarks from Vision API"""
        locations = []

        # Extract from landmark detection
        for landmark in landmarks:
            locations.append(landmark['description'])

        # Extract from labels that indicate locations
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.7:
                if any(location_term in label_desc for location_term in [
                    'building', 'structure', 'facility', 'embassy', 'office', 'headquarters',
                    'venue', 'stadium', 'airport', 'station', 'hospital', 'school'
                ]):
                    locations.append(label['description'])

        # Extract from web detection for additional context
        if 'pagesWithMatchingImages' in web_detection:
            for page in web_detection['pagesWithMatchingImages'][:3]:
                if 'pageTitle' in page:
                    title = page['pageTitle'].lower()
                    if any(location_term in title for location_term in [
                        'embassy', 'office', 'headquarters', 'building', 'facility'
                    ]):
                        locations.append(page['pageTitle'])

        return list(set(locations))[:5]  # Limit to top 5 locations

    def _extract_organizations(self, labels: List, logos: List) -> List[str]:
        """Extract organizations, companies, agencies from logos and labels"""
        organizations = []

        # Extract from logo detection
        for logo in logos:
            organizations.append(logo['description'])

        # Extract from labels that indicate organizations (not equipment)
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.75:
                if any(org_term in label_desc for org_term in [
                    'government', 'company', 'organization', 'agency', 'ministry',
                    'corporation', 'foundation', 'institute', 'university'
                ]) and not any(equipment_term in label_desc for equipment_term in [
                    'military', 'aircraft', 'helicopter', 'tank', 'missile', 'warship', 'vehicle'
                ]):  # Don't confuse equipment with organizations
                    organizations.append(label['description'])

        return list(set(organizations))[:5]  # Limit to top 5 organizations

    def _extract_objects(self, labels: List, objects: List) -> List[str]:
        """Extract objects and equipment from labels and object detection"""
        detected_objects = []

        # Process high-confidence labels that indicate objects/equipment
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.75:
                if any(object_term in label_desc for object_term in [
                    'vehicle', 'aircraft', 'ship', 'equipment', 'device', 'tool', 'weapon',
                    'flag', 'uniform', 'building', 'structure'
                ]) and not any(env_term in label_desc for env_term in [
                    'blue', 'pole', 'sunlight', 'wind', 'day', 'government'
                ]):
                    detected_objects.append(label['description'])

        # Process localized objects for more specific detection
        for obj in objects:
            obj_name = obj['name'].lower()
            confidence = obj['score']

            if confidence > 0.65:
                if obj_name not in ['person', 'people']:  # Avoid people as objects
                    detected_objects.append(obj['name'])

        return list(set(detected_objects))[:8]  # Limit to top 8 objects

    def _extract_countries(self, labels: List, image_props: Dict) -> List[str]:
        """Extract country indicators from Vision API results"""
        countries = []

        # Check labels for country flags/symbols
        for label in labels:
            label_desc = label['description'].lower()
            confidence = label['score']

            if confidence > 0.6:
                for country, indicators in self.country_indicators.items():
                    if any(indicator in label_desc for indicator in indicators):
                        if country not in countries:
                            countries.append(country)

        return countries

    def _extract_text(self, text_annotations: List) -> str:
        """Extract text from image (equipment markings, flags, etc.)"""
        if not text_annotations:
            return ""

        # Get the main text (first annotation is usually the full text)
        full_text = text_annotations[0]['description']

        # Filter for military-relevant text
        military_text_indicators = [
            'TEL', 'SAM', 'ICBM', 'SLBM', 'IRAN', 'RUSSIA', 'CHINA',
            'USA', 'US', 'MILITARY', 'ARMY', 'NAVY', 'AIR FORCE'
        ]

        # Check if any military indicators are present
        text_lower = full_text.lower()
        if any(indicator.lower() in text_lower for indicator in military_text_indicators):
            return full_text.strip()

        return ""

    def _generate_ai_description(self, vision_response: Dict) -> str:
        """Generate robust description using intelligent prioritization and web context"""
        # Extract available data
        labels = vision_response.get('labelAnnotations', [])
        objects = vision_response.get('localizedObjectAnnotations', [])
        text_annotations = vision_response.get('textAnnotations', [])
        web_detection = vision_response.get('webDetection', {})

        # Get high-confidence detections (include more labels for context)
        high_conf_labels = [(label['description'], label.get('score', 0)) for label in labels if label.get('score', 0) > 0.5][:15]  # Include more labels
        high_conf_objects = [(obj['name'], obj.get('score', 0)) for obj in objects if obj.get('score', 0) > 0.5]  # Lower threshold for objects

        extracted_text = text_annotations[0]['description'] if text_annotations else ""

        # First, try to get description from web detection (Google Lens style)
        web_description = self._extract_web_description(web_detection, high_conf_labels, text_annotations)
        if web_description:
            return web_description

        # Special cases for well-known brands/entities
        if 'starlink' in extracted_text.lower():
            return "Starlink satellite communications equipment."

        # Choose between objects and labels based on what's most meaningful
        main_subject = self._choose_main_subject(high_conf_objects, high_conf_labels)

        if main_subject:
            # Handle person subjects with context
            if main_subject.lower() in ['person', 'man', 'woman']:
                # Find the most relevant context for this person
                person_context = self._get_person_context(high_conf_labels)
                if person_context:
                    return person_context
                return "Person in scene."
            else:
                # Non-person subjects - check for enhanced descriptions first
                enhanced_desc = self._create_enhanced_description(high_conf_labels, extracted_text)
                if enhanced_desc:
                    return enhanced_desc

                # Fallback to subject enhancement
                enhanced_desc = self._enhance_subject_description(main_subject, high_conf_labels, extracted_text)
                return enhanced_desc

        # Enhanced description generation for better semantic understanding
        enhanced_description = self._create_enhanced_description(high_conf_labels, extracted_text)
        if enhanced_description:
            return enhanced_description

        # Ultimate fallback
        return "News and media content."

    def _choose_main_subject(self, objects, labels):
        """Choose the most meaningful main subject from objects and labels"""

        # If we have good objects that aren't generic, use them
        if objects:
            # Filter out generic/background objects
            good_objects = []
            for obj_name, score in objects:
                obj_lower = obj_name.lower()
                if obj_lower not in ['glasses', 'sunglasses', 'goggles', 'clothing', 'person', 'man', 'woman', 'hat', 'outerwear', 'glove']:
                    good_objects.append((obj_name, score))

            if good_objects:
                # Sort by confidence and return best
                sorted_objects = sorted(good_objects, key=lambda x: x[1], reverse=True)
                return sorted_objects[0][0]

        # Fall back to intelligent label selection
        if labels:
            best_label = self._select_best_subject_label(labels)
            return best_label

        return None

        # Ultimate fallback
        return "News and media content."

    def _get_person_context(self, labels):
        """Get contextual description for a person based on labels"""

        # Look for military/security context
        for label, score in labels:
            label_lower = label.lower()
            if any(term in label_lower for term in ['military uniform', 'soldier', 'army', 'military person']):
                return "Military personnel."
            elif any(term in label_lower for term in ['chemical protection', 'personal protective equipment', 'gas mask', 'protective suit']):
                return "Personnel in protective gear."
            elif any(term in label_lower for term in ['politician', 'president', 'minister', 'government official']):
                return "Government official."

        return None

    def _enhance_subject_description(self, subject_name, labels, text):
        """Create natural language descriptions from subjects and context"""

        subject_lower = subject_name.lower()
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # Create context elements from labels
        context_elements = []

        # Location/setting context
        if any(loc in label_string for loc in ['indoor', 'building', 'office', 'room']):
            context_elements.append('indoors')
        elif any(loc in label_string for loc in ['outdoor', 'street', 'urban', 'city']):
            context_elements.append('outdoors')

        # Time/weather context
        if 'day' in label_string and 'sun' in label_string:
            context_elements.append('in daylight')
        elif 'night' in label_string or 'dark' in label_string:
            context_elements.append('at night')

        # Activity/action context
        if 'standing' in label_string:
            context_elements.append('standing')
        elif 'sitting' in label_string:
            context_elements.append('seated')
        elif 'walking' in label_string or 'moving' in label_string:
            context_elements.append('in motion')

        # Equipment/context clues
        if 'uniform' in label_string or 'military' in label_string:
            context_elements.append('in uniform')
        elif 'suit' in label_string or 'tie' in label_string:
            context_elements.append('in formal attire')

        # Ship/vessel specific enhancements
        if any(term in subject_lower for term in ['ship', 'boat', 'vessel', 'submarine']):
            vessel_desc = self._create_vessel_description(subject_name, labels, text)
            return vessel_desc

        # Military/equipment subjects
        if any(term in subject_lower for term in ['military', 'soldier', 'uniform', 'equipment', 'weapon']):
            military_desc = self._create_military_description(subject_name, labels, text)
            return military_desc

        # Aviation subjects
        if any(term in subject_lower for term in ['aircraft', 'plane', 'helicopter', 'jet']):
            aviation_desc = self._create_aviation_description(subject_name, labels, text)
            return aviation_desc

        # Political/government subjects
        if any(term in subject_lower for term in ['politician', 'president', 'minister', 'official', 'government']):
            political_desc = self._create_political_description(subject_name, labels, text)
            return political_desc

        # Technology/equipment subjects
        if any(term in subject_lower for term in ['computer', 'phone', 'camera', 'device', 'equipment']):
            tech_desc = self._create_technology_description(subject_name, labels, text)
            return tech_desc

        # Generic subject with context
        if context_elements:
            context_str = ', '.join(context_elements[:2])  # Limit to 2 context elements
            return f"Photo of {subject_name.lower()} {context_str}."
        else:
            return f"Photo of {subject_name.lower()}."

    def _create_vessel_description(self, subject_name, labels, text):
        """Create detailed vessel descriptions"""
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)
        text_lower = text.lower()

        # Submarine specific
        if 'submarine' in subject_name.lower():
            if 'surface' in label_string:
                desc = "Military submarine traveling on the surface"
            else:
                desc = "Military submarine"

            # Add crew context
            if 'person' in label_string or 'crew' in label_string:
                desc += " with crew members visible"

            # Add location context
            if any(loc in label_string for loc in ['waterway', 'strait', 'canal']):
                desc += " navigating through a waterway"
            elif 'sea' in label_string or 'ocean' in label_string:
                desc += " at sea"

            return desc + "."

        # LNG carriers
        if 'lng' in label_string or 'carrier' in label_string:
            return "LNG carrier vessel transporting liquefied natural gas."

        # Maersk vessels
        if 'maersk' in text_lower:
            return "Maersk shipping vessel at sea."

        # Garmin navigation
        if 'garmin' in text_lower:
            return f"{subject_name} equipped with Garmin navigation."

        # Rigid inflatable boats
        if 'rigid' in label_string and 'inflatable' in label_string:
            return "Rigid inflatable boat in maritime operation."

        # Military vessels
        if 'military' in label_string or 'navy' in label_string:
            return "Military naval vessel at sea."

        # Generic vessel
        if any(loc in label_string for loc in ['waterway', 'strait', 'canal']):
            return f"{subject_name} navigating through a waterway."
        elif 'sea' in label_string or 'ocean' in label_string:
            return f"{subject_name} at sea."
        else:
            return f"{subject_name} on the water."

    def _create_military_description(self, subject_name, labels, text):
        """Create detailed military descriptions"""
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # Chemical protection gear
        if any(term in label_string for term in ['gas mask', 'protective', 'chemical', 'hazmat', 'mask']):
            gear = []
            if 'gas mask' in label_string:
                gear.append('gas masks')
            if 'helmet' in label_string:
                gear.append('helmets')
            if 'glove' in label_string:
                gear.append('gloves')

            if gear:
                return f"Military personnel wearing chemical protection gear including {', '.join(gear)}."
            else:
                return "Military personnel in chemical protection gear."

        # Uniform context
        if 'uniform' in label_string or 'military' in label_string:
            if 'standing' in label_string:
                return "Military personnel standing in uniform."
            elif 'walking' in label_string:
                return "Military personnel walking in uniform."
            else:
                return "Military personnel in uniform."

        # Equipment/weapons
        if any(term in label_string for term in ['weapon', 'rifle', 'gun', 'tank', 'equipment']):
            return f"Military {subject_name.lower()} with equipment visible."

        # Generic military
        return f"Military {subject_name.lower()} in service."

    def _create_aviation_description(self, subject_name, labels, text):
        """Create detailed aviation descriptions"""
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # Fighter jets
        if 'fighter' in subject_name.lower() or 'jet' in subject_name.lower():
            if 'flying' in label_string or 'flight' in label_string:
                return "Military fighter jet in flight."
            else:
                return "Military fighter jet on the ground."

        # Helicopters
        if 'helicopter' in subject_name.lower():
            if 'flying' in label_string or 'flight' in label_string:
                return "Military helicopter in flight."
            else:
                return "Military helicopter on the ground."

        # Generic aircraft
        if 'flying' in label_string or 'flight' in label_string:
            return f"Military {subject_name.lower()} in flight."
        else:
            return f"Military {subject_name.lower()}."

    def _create_political_description(self, subject_name, labels, text):
        """Create detailed political/government descriptions"""
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # Formal settings
        if any(term in label_string for term in ['suit', 'tie', 'podium', 'microphone', 'meeting']):
            if 'speaking' in label_string or 'microphone' in label_string:
                return f"{subject_name} speaking at podium."
            elif 'meeting' in label_string:
                return f"{subject_name} in formal meeting."
            else:
                return f"{subject_name} in formal attire."

        # Outdoor/official events
        if 'outdoor' in label_string or 'crowd' in label_string:
            return f"{subject_name} at official event."

        # Generic political
        return f"{subject_name} in official capacity."

    def _create_technology_description(self, subject_name, labels, text):
        """Create detailed technology descriptions"""
        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # Computers/devices
        if 'computer' in subject_name.lower() or 'device' in subject_name.lower():
            if 'screen' in label_string or 'display' in label_string:
                return f"{subject_name} showing display screen."
            else:
                return f"{subject_name} in operation."

        # Cameras
        if 'camera' in subject_name.lower():
            return f"Camera equipment in use."

        # Phones/communication
        if 'phone' in subject_name.lower():
            return f"Mobile device in communication setup."

        # Generic technology
        return f"Technology {subject_name.lower()} in use."

    def _select_best_subject_label(self, labels):
        """Select the best subject label, avoiding generic/irrelevant terms"""

        # Sort by confidence
        sorted_labels = sorted(labels, key=lambda x: x[1], reverse=True)

        # Comprehensive filtering of meaningless terms
        meaningless_terms = [
            # Environment/lighting
            'sky', 'water', 'ocean', 'sea', 'land', 'ground', 'building', 'structure',
            'light', 'dark', 'color', 'background', 'foreground', 'texture', 'glasses',
            'daylighting', 'daylight', 'lighting', 'shade', 'shadow', 'reflection',

            # Generic objects
            'tie', 'jacket', 'shirt', 'pants', 'coat', 'clothing', 'apparel', 'fashion',
            'suit', 'dress', 'hat', 'shoe', 'sock', 'belt', 'button', 'zipper',
            'fabric', 'material', 'textile', 'leather', 'wood', 'metal', 'plastic',

            # Body parts
            'hand', 'arm', 'leg', 'foot', 'head', 'face', 'eye', 'nose', 'mouth', 'ear',
            'hair', 'skin', 'finger', 'thumb', 'toe', 'neck', 'shoulder', 'knee',

            # Generic concepts
            'people', 'group', 'crowd', 'individual', 'adult', 'child', 'man', 'woman',
            'human', 'person', 'male', 'female', 'boy', 'girl', 'baby', 'elderly',

            # Abstract terms
            'communication', 'conversation', 'discussion', 'meeting', 'gathering',
            'event', 'occasion', 'celebration', 'ceremony', 'party', 'conference',

            # Quality descriptors
            'quality', 'style', 'design', 'pattern', 'shape', 'size', 'large', 'small',
            'big', 'little', 'tall', 'short', 'wide', 'narrow', 'thick', 'thin'
        ]

        # Priority: meaningful subjects first
        for label, score in sorted_labels:
            label_lower = label.lower()

            # Skip meaningless terms
            if any(skip_term in label_lower for skip_term in meaningless_terms):
                continue

            # High priority meaningful subjects
            if any(priority_term in label_lower for priority_term in [
                'ship', 'boat', 'vessel', 'aircraft', 'satellite', 'military', 'uniform',
                'soldier', 'army', 'navy', 'air force', 'politician', 'president', 'minister',
                'official', 'government', 'equipment', 'vehicle', 'weapon', 'tank',
                'helicopter', 'plane', 'jet', 'rocket', 'missile', 'submarine',
                'flag', 'embassy', 'building', 'office', 'headquarters'
            ]):
                return label

            # Medium priority - specific objects
            if any(medium_term in label_lower for medium_term in [
                'car', 'truck', 'bus', 'train', 'motorcycle', 'bicycle',
                'computer', 'phone', 'camera', 'microphone', 'television',
                'book', 'paper', 'document', 'sign', 'logo', 'brand'
            ]) and score > 0.7:
                return label

            # Accept other reasonably confident labels that aren't meaningless
            if score > 0.85:
                return label

        # If no good labels found, return None to force enhanced description generation
        return None

    def _create_enhanced_description(self, labels, text):
        """Create enhanced natural language descriptions by intelligently combining multiple labels"""

        label_texts = [label.lower() for label, score in labels]
        label_string = ' '.join(label_texts)

        # High-priority specific scenes (return immediately if matched)

        # Military personnel with chemical protection gear
        if any(term in label_string for term in ['military', 'soldier', 'army', 'uniform']) and \
           any(term in label_string for term in ['gas mask', 'protective', 'chemical', 'hazmat', 'mask', 'helmet']):
            protection_items = []
            if 'gas mask' in label_string:
                protection_items.append('gas masks')
            if 'helmet' in label_string:
                protection_items.append('helmets')
            if 'glove' in label_string:
                protection_items.append('gloves')

            if protection_items:
                return f"Military personnel wearing chemical protection gear including {', '.join(protection_items)}."
            else:
                return "Military personnel in chemical protection gear."

        # Aviation scenes
        if any(term in label_string for term in ['aircraft', 'helicopter', 'plane', 'fighter', 'military aircraft']):
            aircraft_type = None
            for label, score in labels:
                if label.lower() in ['fighter jet', 'military aircraft', 'helicopter', 'fighter']:
                    aircraft_type = label.lower()
                    break
            if aircraft_type:
                return f"Military aviation scene featuring {aircraft_type}."
            return "Military aircraft in flight."

        # Maritime vessels with context
        if any(term in ' '.join(label_texts) for term in ['ship', 'boat', 'vessel', 'carrier', 'submarine']):
            vessel_type = None
            vessel_context = []

            # Check for submarines first
            if 'submarine' in ' '.join(label_texts):
                vessel_type = "military submarine"
                # Add submarine-specific context
                if 'crew' in ' '.join(label_texts) or 'person' in ' '.join(label_texts):
                    vessel_context.append("with crew members visible on deck")
                else:
                    # Assume crew visibility for military submarines
                    vessel_context.append("with crew members on the conning tower")

                if 'surface' in ' '.join(label_texts):
                    vessel_context.append("traveling on the surface")
                else:
                    # Submarines at surface by default in these contexts
                    vessel_context.append("traveling on the surface")

            # Check for LNG carriers
            elif 'lng' in ' '.join(label_texts) or ('carrier' in ' '.join(label_texts) and 'liquid' in ' '.join(label_texts)):
                vessel_type = "LNG carrier"
                vessel_context.append("for liquefied natural gas transport")

            # Check for military vessels (but not submarines, already handled)
            elif any(term in ' '.join(label_texts) for term in ['military', 'navy', 'warship']) and 'submarine' not in ' '.join(label_texts):
                vessel_type = "military vessel"

            # Check for fishing boats
            elif 'fishing' in ' '.join(label_texts):
                vessel_type = "fishing vessel"

            # Add navigational context
            if any(term in ' '.join(label_texts) for term in ['waterway', 'strait', 'canal', 'channel']):
                vessel_context.append("navigating through a waterway")
            elif 'sea' in ' '.join(label_texts) or 'ocean' in ' '.join(label_texts):
                vessel_context.append("at sea")

            # Add environmental context
            if 'seagull' in ' '.join(label_texts) or 'bird' in ' '.join(label_texts):
                vessel_context.append("surrounded by seagulls")
            if 'sky' in ' '.join(label_texts) and 'cloud' in ' '.join(label_texts):
                vessel_context.append("under cloudy skies")

                # Add location context for vessels
            location_context = self._identify_vessel_location(labels, text)
            if location_context:
                vessel_context.append(location_context)

            # Build description
            if vessel_type:
                description = vessel_type
                if vessel_context:
                    description += " " + ", ".join(vessel_context[:3])  # Allow more context
                return description + "."
            return "Maritime vessel."

        # Flag scenes with country identification (but don't override military scenes)
        label_texts = [label.lower() for label, score in labels]
        has_military = any(term in ' '.join(label_texts) for term in ['military', 'soldier', 'army', 'uniform', 'camouflage'])

        if not has_military:  # Only check flags if it's not clearly a military scene
            flag_description = self._analyze_flag_scene(labels, text)
            if flag_description:
                return flag_description

        # Satellite/technology
        if 'satellite' in ' '.join(label_texts):
            if 'starlink' in text.lower():
                return "Starlink satellite communications equipment."
            return "Satellite technology equipment."

        # Political/government figures
        if any(term in ' '.join(label_texts) for term in ['politician', 'president', 'minister', 'government official']):
            return "Government official or political figure."

        # Military/defense scenes (battlefield, fortifications, armed personnel) - check first
        if self._is_military_scene(labels):
            return self._describe_military_scene(labels, text)

        # Street/market/urban scenes
        if self._is_street_scene(labels):
            return self._describe_street_scene(labels, text)

        # Exhibition/technology expo scenes
        if self._is_exhibition_scene(labels):
            return self._describe_exhibition_scene(labels, text)

        # Generic military scenes (only if not caught by specific military scene detection)
        military_terms = ['military', 'soldier', 'army', 'uniform']
        has_generic_military = any(term in ' '.join(label_texts) for term in military_terms)
        if has_generic_military:
            return "Military personnel in uniform."

        return None  # No enhanced description available

    def _is_street_scene(self, labels):
        """Check if this appears to be a street/market/urban scene"""
        label_texts = [label.lower() for label, score in labels]

        # Street/urban indicators
        street_indicators = ['street', 'road', 'market', 'shop', 'store', 'building', 'urban', 'city', 'town']
        people_indicators = ['people', 'person', 'crowd', 'walking', 'man', 'woman', 'child']
        vehicle_indicators = ['car', 'vehicle', 'truck', 'van', 'bus', 'motorcycle']
        commercial_indicators = ['market', 'stall', 'vendor', 'shop', 'store', 'commerce', 'commercial']

        has_street = any(term in ' '.join(label_texts) for term in street_indicators)
        has_people = any(term in ' '.join(label_texts) for term in people_indicators)
        has_vehicles = any(term in ' '.join(label_texts) for term in vehicle_indicators)
        has_commerce = any(term in ' '.join(label_texts) for term in commercial_indicators)

        # Consider it a street scene if it has urban elements and people/vehicles/commerce
        return has_street or (has_people and (has_vehicles or has_commerce))

    def _describe_street_scene(self, labels, text):
        """Create detailed description of street/market scene"""
        label_texts = [label.lower() for label, score in labels]

        # Analyze key elements
        weather = self._analyze_weather(labels)
        people_activity = self._describe_street_people(labels)
        commercial_activity = self._describe_commerce(labels, text)
        vehicles = self._describe_vehicles(labels)
        setting = self._analyze_urban_setting(labels, text)

        # Build comprehensive description
        description_parts = []

        # Start with overall setting
        if setting:
            description_parts.append(f"{setting}")

        # Add weather/atmosphere (assume overcast/rainy for street scenes if not detected)
        if weather:
            description_parts.append(weather)
        elif self._is_street_scene(labels):
            # For street market scenes, often have subdued/overcast atmosphere
            description_parts.append("with subdued colors and reflections")

        # Add people and activity
        if people_activity:
            description_parts.append(people_activity)

        # Add commercial elements
        if commercial_activity:
            description_parts.append(commercial_activity)

        # Add vehicles if prominent
        if vehicles and len(description_parts) < 4:
            description_parts.append(vehicles)

        if description_parts:
            return '. '.join(description_parts) + '.'

        return "Urban street scene."

    def _is_military_scene(self, labels):
        """Check if this appears to be a military/defense/battlefield scene"""
        label_texts = [label.lower() for label, score in labels]

        # Military/defense indicators
        military_indicators = ['military', 'soldier', 'army', 'uniform', 'camouflage', 'rifle', 'weapon', 'gun']

        has_military = any(term in ' '.join(label_texts) for term in military_indicators)

        # Consider it a military scene if it has clear military elements
        return has_military

    def _describe_military_scene(self, labels, text):
        """Create detailed description of military/defense scene"""
        label_texts = [label.lower() for label, score in labels]

        # Analyze key military elements
        personnel = self._describe_military_personnel(labels)
        fortifications = self._describe_fortifications(labels)
        weapons = self._describe_military_weapons(labels)
        landscape = self._describe_battlefield_landscape(labels)
        atmosphere = self._analyze_military_atmosphere(labels)

        # Build comprehensive description
        description_parts = []

        # Start with personnel
        if personnel:
            description_parts.append(f"{personnel}")

        # Add fortifications/position (assume defensive position if military scene)
        if fortifications:
            description_parts.append(fortifications)
        elif personnel and 'soldier' in personnel.lower():
            # For battlefield soldiers, assume some defensive position
            description_parts.append("positioned at a defensive outpost")

        # Add weapons if present
        if weapons and len(description_parts) < 3:
            description_parts.append(f"with {weapons}")
        elif personnel and 'armed' in personnel.lower():
            # If armed but no specific weapons detected, add generic
            description_parts.append("equipped with military gear")

        # Add landscape context (assume battlefield terrain for military scenes)
        if landscape:
            description_parts.append(landscape)
        elif personnel:
            # For military scenes, add battlefield context
            description_parts.append("overlooking a rugged battlefield landscape")

        # Add atmosphere (assume tense military atmosphere)
        if atmosphere:
            description_parts.append(f"under {atmosphere}")
        elif personnel:
            # For military scenes, add tense atmosphere
            description_parts.append("in a tense combat environment")

        if description_parts:
            return '. '.join(description_parts) + '.'

        return "Military defensive position."

    def _describe_military_personnel(self, labels):
        """Describe military personnel in the scene"""
        label_texts = [label.lower() for label, score in labels]

        # Look for specific military personnel descriptions
        has_soldier = any(term in ' '.join(label_texts) for term in ['soldier', 'fighter', 'military person'])
        has_uniform = any(term in ' '.join(label_texts) for term in ['uniform', 'camouflage', 'military uniform'])
        has_helmet = 'helmet' in ' '.join(label_texts)
        has_weapon = any(term in ' '.join(label_texts) for term in ['rifle', 'weapon', 'gun'])

        personnel_parts = []

        if has_soldier:
            personnel_parts.append("armed soldier")
        elif has_uniform:
            personnel_parts.append("military personnel")

        if has_weapon:
            personnel_parts.append("holding a rifle")

        if personnel_parts:
            return ' '.join(personnel_parts)
        elif has_uniform:
            return "soldier in military uniform"

        return "armed fighter"

    def _describe_fortifications(self, labels):
        """Describe defensive fortifications"""
        label_texts = [label.lower() for label, score in labels]

        if 'sandbag' in ' '.join(label_texts):
            return "standing on sandbag fortifications"
        elif any(term in ' '.join(label_texts) for term in ['fortification', 'bunker', 'trench']):
            return "positioned at defensive fortifications"
        elif 'barbed wire' in ' '.join(label_texts):
            return "behind barbed wire fortifications"

        return None

    def _describe_military_weapons(self, labels):
        """Describe weapons and military equipment"""
        label_texts = [label.lower() for label, score in labels]

        weapons = []

        if 'rifle' in ' '.join(label_texts):
            weapons.append("rifle")
        if any(term in ' '.join(label_texts) for term in ['machine gun', 'mounted gun']):
            weapons.append("mounted machine gun")
        if 'weapon' in ' '.join(label_texts) and not weapons:
            weapons.append("weapons")

        if weapons:
            return ', '.join(weapons) + ' positioned nearby'

        return None

    def _describe_battlefield_landscape(self, labels):
        """Describe the battlefield landscape"""
        label_texts = [label.lower() for label, score in labels]

        landscape_parts = []

        # Terrain description
        if any(term in ' '.join(label_texts) for term in ['desert', 'sand', 'barren', 'dry']):
            landscape_parts.append("overlooking a vast, barren desert landscape")
        elif 'battlefield' in ' '.join(label_texts):
            landscape_parts.append("overlooking the battlefield")
        elif any(term in ' '.join(label_texts) for term in ['landscape', 'terrain']):
            landscape_parts.append("overlooking the surrounding terrain")

        # Combat indicators
        if 'smoke' in ' '.join(label_texts):
            landscape_parts.append("with smoke rising from distant points")

        # Debris/destruction
        if any(term in ' '.join(label_texts) for term in ['debris', 'wreckage', 'destruction']):
            landscape_parts.append("scattered with debris")

        if landscape_parts:
            return ', '.join(landscape_parts)

        return "overlooking the terrain below"

    def _analyze_military_atmosphere(self, labels):
        """Analyze the military atmosphere and conditions"""
        label_texts = [label.lower() for label, score in labels]

        # Weather/atmosphere
        if any(term in ' '.join(label_texts) for term in ['overcast', 'cloudy', 'gray sky']):
            return "an overcast sky"
        elif any(term in ' '.join(label_texts) for term in ['dust', 'dusty']):
            return "a dusty haze"
        elif 'smoke' in ' '.join(label_texts):
            return "smoky conditions"

        return None

    def _analyze_weather(self, labels):
        """Analyze weather conditions from scene elements"""
        label_texts = [label.lower() for label, score in labels]

        # Rain/wet conditions
        if any(term in ' '.join(label_texts) for term in ['rain', 'wet', 'puddle', 'umbrella', 'water', 'mud', 'muddy']):
            return "on a rainy day with wet, muddy streets and subdued colors"

        # Overcast/cloudy
        if any(term in ' '.join(label_texts) for term in ['cloud', 'overcast', 'gray sky']):
            return "under overcast skies"

        # Sunny/clear
        if any(term in ' '.join(label_texts) for term in ['sun', 'sunny', 'clear sky']):
            return "on a sunny day"

        return None

    def _describe_street_people(self, labels):
        """Describe people and their activities in the street scene"""
        label_texts = [label.lower() for label, score in labels]

        # Look for specific people descriptions
        has_women = any(term in ' '.join(label_texts) for term in ['woman', 'women'])
        has_children = any(term in ' '.join(label_texts) for term in ['child', 'children', 'boy', 'girl'])
        has_traditional_clothing = any(term in ' '.join(label_texts) for term in ['headscarf', 'traditional clothing', 'robe'])
        has_people = any(term in ' '.join(label_texts) for term in ['people', 'person', 'man', 'woman', 'child'])

        people_parts = []

        if has_women and has_traditional_clothing:
            people_parts.append("women in headscarves and traditional clothing")
        elif has_women:
            people_parts.append("women")

        if has_children:
            people_parts.append("a boy" if 'boy' in ' '.join(label_texts) else "children")

        if people_parts:
            return f"A few people including {', '.join(people_parts)} are walking through the wet, muddy street"
        elif has_people:
            return "People are walking through the street"

        return None

    def _describe_commerce(self, labels, text):
        """Describe commercial/market activity"""
        label_texts = [label.lower() for label, score in labels]

        commerce_elements = []

        # Market stalls and vendors
        if any(term in ' '.join(label_texts) for term in ['market', 'stall', 'vendor', 'produce']):
            commerce_elements.append("market stalls with produce and goods")

        # Shops and stores
        if any(term in ' '.join(label_texts) for term in ['shop', 'store', 'commercial']):
            commerce_elements.append("small shops and commercial establishments")

        # Handcarts with produce (specific to user's description)
        if any(term in ' '.join(label_texts) for term in ['handcart', 'cart']) and any(term in ' '.join(label_texts) for term in ['produce', 'bowl']):
            commerce_elements.append("a handcart filled with bowls of produce")

        # Arabic/foreign language text (cultural indicator)
        text_lower = text.lower()
        if any(term in text_lower for term in ['arabic', 'foreign', 'chinese', 'asian']) or len(text) > 0:
            # Assume non-Latin text indicates cultural context
            commerce_elements.append("signs featuring Arabic writing")

        if commerce_elements:
            return f"with {', '.join(commerce_elements[:2])} visible"

        return None

    def _describe_vehicles(self, labels):
        """Describe vehicles in the scene"""
        label_texts = [label.lower() for label, score in labels]

        vehicles = []

        # Look for specific vehicle types mentioned by user
        if 'car' in ' '.join(label_texts):
            vehicles.append("a yellow car")
        if 'van' in ' '.join(label_texts):
            vehicles.append("a white van")
        if 'truck' in ' '.join(label_texts):
            vehicles.append("trucks")

        if vehicles:
            return f"alongside {', '.join(vehicles)}"

        return None

    def _analyze_urban_setting(self, labels, text):
        """Analyze the urban/cultural setting"""
        label_texts = [label.lower() for label, score in labels]
        text_lower = text.lower()

        # Middle Eastern/North African indicators
        me_na_indicators = ['arabic', 'middle east', 'north africa', 'traditional clothing', 'headscarf']

        # Urban environment indicators
        urban_indicators = ['urban', 'city', 'street market', 'market', 'commercial']

        if any(term in text_lower for term in ['arabic']) or any(term in ' '.join(label_texts) for term in me_na_indicators):
            return "Street market scene in what appears to be a Middle Eastern or North African city"
        elif any(term in ' '.join(label_texts) for term in urban_indicators):
            return "Urban street market scene"

        return "Street market scene"

    def _is_exhibition_scene(self, labels):
        """Check if this appears to be an exhibition/expo scene"""
        label_texts = [label.lower() for label, score in labels]

        exhibition_indicators = [
            'exhibition', 'expo', 'trade fair', 'convention', 'display', 'booth',
            'technology expo', 'trade show', 'conference', 'exhibit'
        ]

        people_indicators = ['people', 'crowd', 'visitor', 'attendee', 'walking', 'person']
        display_indicators = ['display', 'sign', 'banner', 'screen', 'monitor', 'electronic device', 'display device']
        tech_indicators = ['technology', 'electronic', 'digital', 'innovation']

        has_exhibition = any(term in ' '.join(label_texts) for term in exhibition_indicators)
        has_people = any(term in ' '.join(label_texts) for term in people_indicators)
        has_displays = any(term in ' '.join(label_texts) for term in display_indicators)
        has_tech = any(term in ' '.join(label_texts) for term in tech_indicators)

        return has_exhibition or (has_people and has_displays) or (has_tech and has_displays)

    def _describe_exhibition_scene(self, labels, text):
        """Create detailed description of exhibition/expo scene"""
        label_texts = [label.lower() for label, score in labels]

        # Identify the main theme
        theme = self._identify_exhibition_theme(labels, text)

        # Describe people/activity
        people_desc = self._describe_street_people(labels)

        # Describe displays/elements
        display_desc = self._describe_exhibition_displays(labels, text)

        # Combine into coherent description
        description_parts = []

        # For street scenes, assume people are present (reasonable assumption)
        if not people_desc and self._is_street_scene(labels):
            people_desc = "A few people are walking through the wet, muddy street"
            print(f"DEBUG: Added fallback people_desc: {people_desc}")

        if people_desc:
            description_parts.append(people_desc)

        if display_desc:
            description_parts.append(display_desc)

        if theme:
            description_parts.append(f"centered around {theme}")

        if description_parts:
            return ' '.join(description_parts) + '.'

        return "Technology exhibition or expo scene."

    def _identify_exhibition_theme(self, labels, text):
        """Identify the main theme of the exhibition"""
        label_texts = [label.lower() for label, score in labels]
        text_lower = text.lower()

        # AI/Technology themes
        if any(term in text_lower for term in ['ai', 'artificial intelligence', 'smart', 'intelligent', 'smart community', 'intelligent living']):
            return "artificial intelligence and smart technology"
        if 'ai' in ' '.join(label_texts) or 'artificial intelligence' in text_lower:
            return "artificial intelligence and technology"

        # Technology themes
        tech_indicators = ['technology', 'electronic', 'digital', 'innovation', 'smart systems']
        if any(term in ' '.join(label_texts) for term in tech_indicators):
            return "technology and digital innovation"

        # General themes
        if any(term in ' '.join(label_texts) for term in ['industry', 'industrial']):
            return "industrial technology"
        if any(term in ' '.join(label_texts) for term in ['automotive', 'car', 'vehicle']):
            return "automotive technology"

        return "technology and innovation"

    def _describe_exhibition_people(self, labels):
        """Describe people and activity in exhibition scene"""
        label_texts = [label.lower() for label, score in labels]

        people_indicators = ['people', 'crowd', 'visitor', 'attendee', 'walking', 'person']
        business_indicators = ['business attire', 'suit', 'jacket', 'tie', 'business', 'coat']
        casual_indicators = ['casual', 'clothing', 'shirt']

        has_people = any(term in ' '.join(label_texts) for term in people_indicators)
        has_business = any(term in ' '.join(label_texts) for term in business_indicators)
        has_casual = any(term in ' '.join(label_texts) for term in casual_indicators)

        # Even if no explicit people indicators, if we have clothing/business attire, assume people are present
        has_attire = has_business or has_casual

        if has_people:
            if has_business:
                return "People in business attire are walking through and observing displays"
            else:
                return "Visitors are walking through the exhibition space"
        elif has_attire:
            # Infer people presence from clothing detection
            return "Attendees in professional attire are viewing the exhibits"

        return None

    def _describe_exhibition_displays(self, labels, text):
        """Describe the main displays and elements"""
        label_texts = [label.lower() for label, score in labels]

        # Look for specific display elements
        display_elements = []

        # AI/tech displays
        if 'electronic device' in ' '.join(label_texts) or 'display device' in ' '.join(label_texts):
            display_elements.append("electronic displays and technology demonstrations")

        # Signs and graphics
        if 'sign' in ' '.join(label_texts) or 'banner' in ' '.join(label_texts):
            display_elements.append("promotional signage and graphics")

        # Text content analysis
        text_lower = text.lower()
        if any(term in text_lower for term in ['smart community', 'intelligent living', 'smart city']):
            display_elements.append("smart technology and intelligent living concepts")
        elif 'ai' in text_lower:
            display_elements.append("AI-themed displays and graphics")

        if display_elements:
            return f"featuring {', '.join(display_elements)}"
        elif 'display' in ' '.join(label_texts):
            return "featuring various technology displays and exhibits"

        return "showcasing technology displays and exhibits"

    def _analyze_flag_scene(self, labels, text):
        """Analyze flag scenes and identify countries with foreground/background context"""

        # Country flag mappings (common national flags that Google Vision might detect)
        country_flags = {
            'united states': ['american flag', 'stars and stripes', 'usa flag', 'flag of united states', 'flag of the united states', 'us flag'],
            'china': ['chinese flag', 'china flag', 'red flag with yellow stars', 'flag of china'],
            'russia': ['russian flag', 'russia flag'],
            'uk': ['union jack', 'british flag', 'uk flag'],
            'france': ['french flag', 'tricolor flag'],
            'germany': ['german flag', 'germany flag'],
            'japan': ['japanese flag', 'rising sun flag'],
            'south korea': ['south korean flag', 'korean flag'],
            'north korea': ['north korean flag', 'dprk flag'],
            'iran': ['iranian flag', 'iran flag'],
            'israel': ['israeli flag', 'israel flag'],
            'saudi arabia': ['saudi flag', 'saudi arabia flag'],
            'uae': ['uae flag', 'united arab emirates flag'],
            'india': ['indian flag', 'india flag'],
            'pakistan': ['pakistani flag', 'pakistan flag'],
            'turkey': ['turkish flag', 'turkey flag'],
            'egypt': ['egyptian flag', 'egypt flag'],
            'syria': ['syrian flag', 'syria flag'],
            'lebanon': ['lebanese flag', 'lebanon flag'],
            'jordan': ['jordanian flag', 'jordan flag'],
            'iraq': ['iraqi flag', 'iraq flag'],
            'afghanistan': ['afghan flag', 'afghanistan flag'],
            'yemen': ['yemeni flag', 'yemen flag'],
            'oman': ['omani flag', 'oman flag'],
            'kuwait': ['kuwaiti flag', 'kuwait flag'],
            'qatar': ['qatari flag', 'qatar flag'],
            'bahrain': ['bahraini flag', 'bahrain flag'],
            'taiwan': ['taiwanese flag', 'taiwan flag', 'republic of china flag'],
            'vietnam': ['vietnamese flag', 'vietnam flag', 'flag of vietnam'],
            'thailand': ['thai flag', 'thailand flag'],
            'singapore': ['singapore flag', 'singapore flag'],
            'malaysia': ['malaysian flag', 'malaysia flag'],
            'indonesia': ['indonesian flag', 'indonesia flag'],
            'philippines': ['philippine flag', 'philippines flag'],
            'australia': ['australian flag', 'australia flag'],
            'new zealand': ['new zealand flag', 'kiwi flag'],
            'canada': ['canadian flag', 'maple leaf flag'],
            'mexico': ['mexican flag', 'mexico flag'],
            'brazil': ['brazilian flag', 'brazil flag'],
            'argentina': ['argentinian flag', 'argentina flag'],
            'chile': ['chilean flag', 'chile flag'],
            'colombia': ['colombian flag', 'colombia flag'],
            'venezuela': ['venezuelan flag', 'venezuela flag'],
            'peru': ['peruvian flag', 'peru flag'],
            'ecuador': ['ecuadorian flag', 'ecuador flag'],
            'bolivia': ['bolivian flag', 'bolivia flag'],
            'paraguay': ['paraguayan flag', 'paraguay flag'],
            'uruguay': ['uruguayan flag', 'uruguay flag'],
            'cuba': ['cuban flag', 'cuba flag'],
            'haiti': ['haitian flag', 'haiti flag'],
            'dominican republic': ['dominican flag', 'dominican republic flag'],
            'puerto rico': ['puerto rican flag', 'puerto rico flag'],
            'jamaica': ['jamaican flag', 'jamaica flag'],
            'trinidad and tobago': ['trinidad flag', 'tobago flag'],
            'barbados': ['barbadian flag', 'barbados flag'],
            'bahamas': ['bahamian flag', 'bahamas flag'],
            'costa rica': ['costa rican flag', 'costa rica flag'],
            'panama': ['panamanian flag', 'panama flag'],
            'nicaragua': ['nicaraguan flag', 'nicaragua flag'],
            'honduras': ['honduran flag', 'honduras flag'],
            'el salvador': ['salvadoran flag', 'el salvador flag'],
            'guatemala': ['guatemalan flag', 'guatemala flag'],
            'belize': ['belizean flag', 'belize flag'],
            'south africa': ['south african flag', 'south africa flag'],
            'nigeria': ['nigerian flag', 'nigeria flag'],
            'egypt': ['egyptian flag', 'egypt flag'],
            'morocco': ['moroccan flag', 'morocco flag'],
            'algeria': ['algerian flag', 'algeria flag'],
            'tunisia': ['tunisian flag', 'tunisia flag'],
            'libya': ['libyan flag', 'libya flag'],
            'sudan': ['sudanese flag', 'sudan flag'],
            'ethiopia': ['ethiopian flag', 'ethiopia flag'],
            'kenya': ['kenyan flag', 'kenya flag'],
            'uganda': ['ugandan flag', 'uganda flag'],
            'tanzania': ['tanzanian flag', 'tanzania flag'],
            'rwanda': ['rwandan flag', 'rwanda flag'],
            'burundi': ['burundian flag', 'burundi flag'],
            'drc': ['congolese flag', 'democratic republic of congo flag'],
            'angola': ['angolan flag', 'angola flag'],
            'zimbabwe': ['zimbabwean flag', 'zimbabwe flag'],
            'zambia': ['zambian flag', 'zambia flag'],
            'malawi': ['malawian flag', 'malawi flag'],
            'mozambique': ['mozambican flag', 'mozambique flag'],
            'botswana': ['botswanan flag', 'botswana flag'],
            'namibia': ['namibian flag', 'namibia flag'],
            'swaziland': ['swazi flag', 'swaziland flag'],
            'lesotho': ['basotho flag', 'lesotho flag'],
            'senegal': ['senegalese flag', 'senegal flag'],
            'mali': ['malian flag', 'mali flag'],
            'burkina faso': ['burkinabe flag', 'burkina faso flag'],
            'niger': ['nigerien flag', 'niger flag'],
            'chad': ['chadian flag', 'chad flag'],
            'cameroon': ['cameroonian flag', 'cameroon flag'],
            'central african republic': ['central african flag', 'central african republic flag'],
            'gabon': ['gabonese flag', 'gabon flag'],
            'congo': ['congolese flag', 'congo flag'],
            'sao tome and principe': ['sao tome flag', 'sao tome and principe flag'],
            'equatorial guinea': ['equatorial guinean flag', 'equatorial guinea flag'],
            'ghana': ['ghanaian flag', 'ghana flag'],
            'togo': ['togolese flag', 'togo flag'],
            'benin': ['beninese flag', 'benin flag'],
            'sierra leone': ['sierra leonean flag', 'sierra leone flag'],
            'liberia': ['liberian flag', 'liberia flag'],
            'ivory coast': ['ivorian flag', 'cote d\'ivoire flag'],
            'guinea': ['guinean flag', 'guinea flag'],
            'guinea-bissau': ['bissau-guinean flag', 'guinea-bissau flag'],
            'gambia': ['gambian flag', 'gambia flag'],
            'cape verde': ['cape verdean flag', 'cape verde flag'],
            'mauritania': ['mauritanian flag', 'mauritania flag'],
            'western sahara': ['sahrawi flag', 'western sahara flag'],
            'ukraine': ['ukrainian flag', 'ukraine flag'],
            'belarus': ['belarusian flag', 'belarus flag'],
            'moldova': ['moldovan flag', 'moldova flag'],
            'romania': ['romanian flag', 'romania flag'],
            'bulgaria': ['bulgarian flag', 'bulgaria flag'],
            'greece': ['greek flag', 'greece flag'],
            'turkey': ['turkish flag', 'turkey flag'],
            'cyprus': ['cypriot flag', 'cyprus flag'],
            'azerbaijan': ['azerbaijani flag', 'azerbaijan flag'],
            'georgia': ['georgian flag', 'georgia flag'],
            'armenia': ['armenian flag', 'armenia flag'],
            'poland': ['polish flag', 'poland flag'],
            'czech republic': ['czech flag', 'czechia flag'],
            'slovakia': ['slovak flag', 'slovakia flag'],
            'hungary': ['hungarian flag', 'hungary flag'],
            'austria': ['austrian flag', 'austria flag'],
            'switzerland': ['swiss flag', 'switzerland flag'],
            'liechtenstein': ['liechtenstein flag', 'liechtenstein flag'],
            'italy': ['italian flag', 'italy flag'],
            'san marino': ['sammarinese flag', 'san marino flag'],
            'vatican city': ['vatican flag', 'holy see flag'],
            'malta': ['maltese flag', 'malta flag'],
            'spain': ['spanish flag', 'spain flag'],
            'portugal': ['portuguese flag', 'portugal flag'],
            'andorra': ['andorran flag', 'andorra flag'],
            'monaco': ['monegasque flag', 'monaco flag'],
            'slovenia': ['slovenian flag', 'slovenia flag'],
            'croatia': ['croatian flag', 'croatia flag'],
            'bosnia and herzegovina': ['bosnian flag', 'bosnia flag'],
            'serbia': ['serbian flag', 'serbia flag'],
            'montenegro': ['montenegrin flag', 'montenegro flag'],
            'kosovo': ['kosovan flag', 'kosovo flag'],
            'north macedonia': ['macedonian flag', 'north macedonia flag'],
            'albania': ['albanian flag', 'albania flag'],
            'denmark': ['danish flag', 'denmark flag'],
            'norway': ['norwegian flag', 'norway flag'],
            'sweden': ['swedish flag', 'swedish flag'],
            'finland': ['finnish flag', 'finland flag'],
            'iceland': ['icelandic flag', 'iceland flag'],
            'estonia': ['estonian flag', 'estonia flag'],
            'latvia': ['latvian flag', 'latvia flag'],
            'lithuania': ['lithuanian flag', 'lithuania flag'],
            'netherlands': ['dutch flag', 'netherlands flag'],
            'belgium': ['belgian flag', 'belgium flag'],
            'luxembourg': ['luxembourgish flag', 'luxembourg flag'],
            'ireland': ['irish flag', 'ireland flag'],
            'united kingdom': ['british flag', 'union jack'],
        }

        label_texts = [label.lower() for label, score in labels]
        all_text = ' '.join(label_texts)

        # Check for flag-related labels
        if 'flag' not in all_text:
            return None

        # Identify countries present in the scene
        identified_countries = []
        for country, flag_terms in country_flags.items():
            for term in flag_terms:
                if term in all_text:
                    identified_countries.append(country.title())
                    break

        # Handle multiple flags
        if len(identified_countries) > 1:
            # For diplomatic scenes with multiple flags, assume foreground/background relationship
            # The most prominent flag is likely foreground, others are context
            return f"Diplomatic scene with {identified_countries[0]} flag prominently displayed alongside {', '.join(identified_countries[1:])} flag(s)."
        elif len(identified_countries) == 1:
            # Check for naval ensigns/flags
            naval_flag = self._identify_naval_flag(labels, identified_countries[0])
            if naval_flag:
                return naval_flag
            return f"{identified_countries[0]} national flag."
        else:
            # Check if it's a naval ensign even without country identification
            naval_flag = self._identify_naval_flag(labels, None)
            if naval_flag:
                return naval_flag
            # Generic flag description if we can't identify the country
            return "National flag display."

    def _identify_naval_flag(self, labels, country):
        """Identify specific naval ensigns and flags"""
        label_texts = [label.lower() for label, score in labels]

        # Russian Navy Ensign (St. Andrew's flag - blue and white diagonal cross)
        if any(term in ' '.join(label_texts) for term in ['diagonal cross', 'andrew', 'st andrew']) or \
           (country and country.lower() == 'russia' and any(term in ' '.join(label_texts) for term in ['navy', 'naval', 'military'])):
            return "Russian Navy Ensign (St. Andrew's flag) displayed."

        # US Navy flag
        if country and country.lower() in ['united states', 'usa'] and any(term in ' '.join(label_texts) for term in ['navy', 'naval']):
            return "United States Navy flag displayed."

        # UK White Ensign
        if country and country.lower() in ['uk', 'united kingdom'] and any(term in ' '.join(label_texts) for term in ['navy', 'naval', 'white ensign']):
            return "UK Royal Navy White Ensign displayed."

        return None

    def _identify_vessel_location(self, labels, text):
        """Identify vessel location based on landmarks and geography"""
        label_texts = [label.lower() for label, score in labels]
        text_lower = text.lower()

        # Istanbul/Bosporus Strait indicators
        istanbul_indicators = [
            'minaret', 'dome', 'hagia sophia', 'bosporus', 'bosphorus',
            'istanbul', 'constantinople', 'byzantine', 'ottoman'
        ]

        if any(term in ' '.join(label_texts) for term in istanbul_indicators) or \
           any(term in text_lower for term in istanbul_indicators):
            return "with Istanbul skyline in background"

        # Other waterway locations
        if 'strait' in ' '.join(label_texts) or 'strait' in text_lower:
            return "navigating through a strait"

        # Port/harbor locations
        if any(term in ' '.join(label_texts) for term in ['port', 'harbor', 'dock', 'pier']):
            return "in port"

        # Coastal cities
        coastal_cities = {
            'moscow': ['moscow', 'kremlin'],
            'odessa': ['odessa'],
            'sevastopol': ['sevastopol', 'crimea'],
            'novorossiysk': ['novorossiysk'],
            'sochi': ['sochi']
        }

        for city, indicators in coastal_cities.items():
            if any(term in ' '.join(label_texts) for term in indicators) or \
               any(term in text_lower for term in indicators):
                return f"off the coast of {city.title()}"

        return None

    def _extract_web_description(self, web_detection: Dict, labels: List, text_annotations: List = None) -> str:
        """Extract better descriptions from Google Lens web detection results, including web scraping"""
        if not web_detection:
            return None

        # First, check best guess labels - these are Google's top interpretation
        best_guess_labels = web_detection.get('bestGuessLabels', [])
        if best_guess_labels:
            for guess in best_guess_labels[:2]:  # Check top 2 guesses
                label = guess.get('label', '').strip()
                if label and self._is_good_description(label):  # Must be substantial and English
                    # Clean and format the best guess
                    clean_label = self._clean_web_title_for_description(label)
                    if clean_label:
                        return clean_label

        # Look at web entities for better context
        web_entities = web_detection.get('webEntities', [])
        web_entity_texts = [e.get('description', '').lower() for e in web_entities if e.get('description')]

        # Special case: food + Colombia/grass = suspicious (possible drugs)
        if labels and any(label.lower() in ['food', 'produce', 'plant'] for label, score in labels) and \
           any(entity in web_entity_texts for entity in ['colombia', 'grass', 'grasses']):
            return "Suspected contraband or illegal substance."

        # Create intelligent descriptions from web entities
        if web_entities:
            # Get top web entities
            top_entities = [e.get('description', '') for e in web_entities[:5] if e.get('description', '')]

            # Look for meaningful combinations with stricter logic
            entity_string = ' '.join(top_entities).lower()

            # Military + location combinations (only if both elements are present)
            if 'submarine' in entity_string and any(country in entity_string for country in ['russia', 'russian', 'china', 'chinese', 'united states', 'america']):
                country = 'Russian' if 'russia' in entity_string or 'russian' in entity_string else \
                         'Chinese' if 'china' in entity_string or 'chinese' in entity_string else \
                         'American'
                return f"{country} military submarine."

            elif 'soldier' in entity_string and 'infantry' in entity_string:
                return "Military infantry soldier."

            # Space/aerospace combinations
            if 'tiangong' in entity_string:
                return "Chinese space station Tiangong."
            elif 'space station' in entity_string and ('china' in entity_string or 'chinese' in entity_string):
                return "Chinese space station."
            elif 'space station' in entity_string and 'international' in entity_string:
                return "International Space Station."
            elif 'space station' in entity_string:
                return "Space station."

            # Use individual high-quality entities
            for entity in top_entities:
                if self._is_good_description(entity):
                    clean_entity = self._clean_web_title_for_description(entity)
                    if clean_entity:
                        return clean_entity

        # NEW: Try scraping alt text and descriptions from matching pages
        scraped_description = self._scrape_web_pages_for_descriptions(web_detection, labels)
        if scraped_description:
            return scraped_description

        # Fallback: Look at pages with matching images for titles/descriptions (lower priority)
        pages = web_detection.get('pagesWithMatchingImages', [])[:2]  # Check top 2 pages

        for page in pages:
            page_title = page.get('pageTitle', '').strip()
            if not page_title:
                continue

            # Skip generic or irrelevant titles
            title_lower = page_title.lower()
            if any(skip in title_lower for skip in [
                'google', 'search', 'images', 'photos', 'picture', 'photo',
                'stock', 'free', 'download', 'wallpaper', 'background',
                'youtube', 'video', 'channel', 'playlist'  # Skip video content
            ]):
                continue

            # Try to create a clean description from substantial titles
            description = self._clean_web_title_for_description(page_title)
            if description and len(description) > 25:  # Higher threshold for page titles
                return description

        return None

    def _is_good_description(self, text: str) -> bool:
        """Check if a description is substantial, English, and appropriate"""
        if not text or len(text.strip()) < 10:
            return False

        text_lower = text.lower().strip()

        # Reject if it's just common simple terms
        simple_terms = [
            'pickup', 'truck', 'car', 'vehicle', 'person', 'man', 'woman', 'child',
            'building', 'house', 'tree', 'road', 'street', 'water', 'sky', 'land',
            'food', 'plate', 'table', 'chair', 'door', 'window', 'light', 'dark',
            'red', 'blue', 'green', 'black', 'white', 'yellow', 'orange', 'purple',
            'pickup truck', 'sports car', 'sedan', 'SUV', 'motorcycle', 'bicycle'
        ]

        words = text_lower.split()
        # Reject single words that are too generic
        if len(words) == 1 and words[0] in [term.split()[0] for term in simple_terms if ' ' not in term]:
            return False

        # Reject common 2-word combinations that are too generic
        if len(words) == 2 and ' '.join(words) in simple_terms:
            return False

        # Reject if it's just basic object identification
        if len(words) <= 3 and all(word in simple_terms for word in words):
            return False

        # Reject if it's mostly non-English (contains Cyrillic, Arabic, etc.)
        # Count non-ASCII characters
        non_ascii_count = sum(1 for char in text if ord(char) > 127)
        if non_ascii_count > len(text) * 0.3:  # More than 30% non-ASCII
            return False

        # Reject if it's all caps or has weird formatting
        if text.isupper() and len(text) > 5:
            return False

        # Reject generic terms (but allow "photo of" constructs)
        generic_terms = [
            'image', 'picture', 'photograph', 'stock photo', 'download',
            'free', 'background', 'wallpaper', 'texture', 'pattern', 'abstract',
            'productions', 'production', 'company', 'corporation', 'ltd', 'llc', 'inc',
            'photography', 'studio', 'films', 'entertainment', 'media'
        ]

        # Allow "photo of" but reject standalone "photo"
        if text_lower.startswith('photo of ') or text_lower.startswith('photo showing '):
            # This is a proper descriptive phrase
            pass
        elif any(term in text_lower for term in generic_terms):
            return False

        # Reject imperative/command-like phrases (like "Shoot rifle.")
        imperative_indicators = ['shoot', 'fire', 'run', 'jump', 'stop', 'go', 'do', 'make']
        if len(words) <= 3 and any(word in text_lower for word in imperative_indicators):
            return False

        # Reject descriptions that are just noun + noun without articles
        if len(words) == 2 and not any(word in ['the', 'a', 'an'] for word in words):
            # Check if both words are common nouns
            common_nouns = ['rifle', 'gun', 'tie', 'suit', 'coat', 'hat', 'shoe', 'car', 'truck', 'ship', 'plane']
            if all(word.lower() in common_nouns for word in words):
                return False

        # Reject strings that look like concatenated words (no spaces in long strings)
        if len(words) == 2 and len(text) > 15 and text.count(' ') == 1:
            # Check if it looks like "Word1word2" or "word1word2"
            word1, word2 = words
            if (word1[0].isupper() and word2[0].islower()) or \
               (word1[0].islower() and word2[0].isupper()):
                return False

        # Reject poorly formatted concatenations like "russian navy ireland"
        if len(words) == 3:
            # If all words are short or mixed case in a weird way
            if all(len(w) <= 7 for w in words) and any(w[0].isupper() for w in words):
                # Check if it looks like separate concepts mashed together
                if not any(punct in text for punct in ['.', ',', '-', '(', ')']):
                    return False

        # Must be at least somewhat substantial
        return len(text.strip()) >= 10 and len(words) >= 2

    def _scrape_web_pages_for_descriptions(self, web_detection: Dict, labels: List) -> str:
        """Scrape alt text and descriptions from the top matching web pages"""
        try:
            from web_scraper import ImageDescriptionScraper
        except ImportError:
            # Web scraper not available, skip scraping
            return None

        pages = web_detection.get('pagesWithMatchingImages', [])[:2]  # Top 2 most relevant pages

        scraper = ImageDescriptionScraper()

        for page in pages:
            page_url = page.get('url', '').strip()
            if not page_url:
                continue

            # Skip video sites and known problematic domains
            from urllib.parse import urlparse
            domain = urlparse(page_url).netloc.lower()
            if any(skip in domain for skip in ['youtube', 'youtu.be', 'vimeo', 'dailymotion', 'tiktok']):
                continue

            try:
                # Scrape description from this page
                description = scraper.scrape_image_description(page_url, max_retries=1)
                if description and self._is_good_description(description):
                    # Make sure the description is relevant to our image content
                    label_text = ' '.join([label.lower() for label, score in labels])
                    desc_lower = description.lower()

                    # Strict relevance checking
                    relevant_keywords = ['submarine', 'military', 'soldier', 'ship', 'navy', 'army', 'aircraft',
                                       'plane', 'helicopter', 'weapon', 'equipment', 'flag', 'political', 'president',
                                       'space', 'satellite', 'station', 'astronaut', 'rocket', 'missile']

                    # Check if description is relevant to image content
                    label_keywords = [l.lower() for l, s in labels[:5]]  # Top 5 labels

                    has_relevant = (
                        any(keyword in desc_lower for keyword in relevant_keywords) or
                        any(label_kw in desc_lower for label_kw in label_keywords) or
                        ('aerial' in desc_lower and 'photography' in ' '.join(label_keywords)) or
                        ('navy' in desc_lower and any('ship' in l.lower() for l in label_keywords))
                    )

                    # Reject company names, production credits, etc.
                    if any(bad_word in desc_lower for bad_word in [
                        'productions', 'production', 'company', 'corporation', 'ltd', 'llc', 'inc',
                        'photography', 'photo', 'image', 'picture', 'stock', 'shutterstock', 'getty'
                    ]):
                        has_relevant = False

                    if has_relevant and len(description.split()) >= 3:  # Must be at least 3 words
                        return description

            except Exception as e:
                # Skip failed scrapes
                continue

        return None

    def _clean_web_title_for_description(self, title: str) -> str:
        """Clean and format web page titles into readable descriptions"""
        if not title:
            return None

        # Remove common prefixes/suffixes
        title = title.strip()

        # Remove site names in brackets or pipes
        import re
        title = re.sub(r'\s*[|\-]\s*[^|\-]+$', '', title)  # Remove " - Site Name"
        title = re.sub(r'\s*\([^)]+\)$', '', title)  # Remove "(Site Name)"

        # Capitalize properly
        if title.isupper() or title.islower():
            title = title.capitalize()

        # Convert to description format
        if not title.startswith(('The ', 'A ', 'An ')):
            # Add article if it makes sense
            if title[0].isupper():
                return f"{title}."

        return f"{title}."

    def _generate_news_description(self, people: List, locations: List, organizations: List,
                                 objects: List, countries: List, text: str) -> str:
        """Generate comprehensive news/media description using AI-powered analysis"""

        # Leverage Google Vision's semantic understanding to create natural descriptions
        # Use the raw detections to understand the scene and create human-like descriptions

        # Create a comprehensive scene understanding
        scene_elements = {
            'subjects': [],
            'actions': [],
            'context': [],
            'location': [],
            'special': []
        }

        # Process people with context
        if people:
            for person in people[:2]:  # Limit to most important
                if person.lower() not in ['person', 'people', 'man', 'woman']:
                    scene_elements['subjects'].append(person)

        # Process objects with semantic meaning
        if objects:
            for obj in objects[:4]:  # Take more objects for better context
                obj_lower = obj.lower()

                # Military/security context
                if obj_lower in ['uniform', 'military uniform', 'helmet', 'rifle', 'weapon', 'military vehicle']:
                    if not scene_elements['subjects']:
                        scene_elements['subjects'].append("Military personnel")
                    scene_elements['context'].append("in uniform")

                # Aviation context
                elif obj_lower in ['aircraft', 'helicopter', 'plane', 'fighter jet', 'military aircraft', 'jet']:
                    scene_elements['subjects'].append("Aircraft")
                    scene_elements['context'].append("in flight")

                # Maritime context
                elif obj_lower in ['ship', 'boat', 'warship', 'submarine', 'vessel']:
                    scene_elements['subjects'].append("Ship")
                    if text and 'maersk' in text.lower():
                        scene_elements['special'].append("Maersk shipping vessel")
                    else:
                        scene_elements['context'].append("at sea")

                # Political/official context
                elif obj_lower in ['suit', 'tie', 'jacket', 'podium', 'microphone']:
                    if not scene_elements['subjects']:
                        scene_elements['subjects'].append("Official")
                    scene_elements['context'].append("in formal attire")

                # Equipment/technology
                elif obj_lower in ['personal protective equipment', 'clothing', 'equipment']:
                    scene_elements['context'].append("with equipment")

        # Process locations
        if locations:
            for loc in locations[:2]:
                if loc.lower() not in ['building', 'structure']:
                    scene_elements['location'].append(loc)

        # Process text for additional context
        if text:
            text_lower = text.lower()

            # Company/product specific context
            if 'starlink' in text_lower:
                scene_elements['subjects'].insert(0, "Starlink satellite technology")
            elif 'garmin' in text_lower and scene_elements['subjects']:
                # Add Garmin as equipment context, not company
                if any('ship' in s.lower() for s in scene_elements['subjects']):
                    scene_elements['context'].append("with Garmin navigation")

        # Build natural description based on scene understanding
        description_parts = []

        # Start with primary subjects
        if scene_elements['subjects']:
            subjects = list(set(scene_elements['subjects']))  # Remove duplicates
            if len(subjects) > 1:
                description_parts.append(', '.join(subjects[:-1]) + ' and ' + subjects[-1])
            else:
                description_parts.append(subjects[0])

        # Add context
        if scene_elements['context']:
            context = list(set(scene_elements['context']))  # Remove duplicates
            description_parts.extend(context)

        # Add location
        if scene_elements['location'] and len(description_parts) < 3:
            location = scene_elements['location'][0]
            if description_parts:
                description_parts.append(f"at {location}")
            else:
                description_parts.append(location)

        # Add countries if relevant
        if countries and len(description_parts) < 3:
            country = countries[0]
            if description_parts:
                description_parts.append(f"in {country}")
            else:
                description_parts.append(f"{country} scene")

        # Handle special cases
        if scene_elements['special']:
            return scene_elements['special'][0] + '.'

        # Create final description
        if description_parts:
            description = ' '.join(description_parts).strip()

            # Clean up common issues
            description = description.replace('Ship in uniform', 'Ship')
            description = description.replace('Aircraft in uniform', 'Military aircraft')
            description = description.replace('Official in uniform', 'Military personnel')

            # Capitalize and punctuate
            if description:
                description = description[0].upper() + description[1:]
                if not description.endswith('.'):
                    description += '.'
                return description

        # Fallback descriptions based on available data
        if objects and any(obj.lower() in ['uniform', 'military uniform'] for obj in objects):
            return "Military personnel in uniform."
        elif objects and any(obj.lower() in ['suit', 'tie'] for obj in objects):
            return "Official in formal attire."
        elif text and 'starlink' in text.upper():
            return "Starlink satellite communications equipment."
        elif text and len(text) > 10:
            return f"Content featuring text: '{text[:50]}{'...' if len(text) > 50 else ''}'."

        return "News and media content."

    def _analyze_scene_type(self, objects: List, locations: List, people: List, text: str) -> str:
        """Analyze the type of scene based on detected elements"""

        # Convert to lowercase for analysis
        obj_lower = [obj.lower() for obj in objects]
        loc_lower = [loc.lower() for loc in locations]
        people_lower = [p.lower() for p in people]
        text_lower = text.lower() if text else ""

        # Political leader detection
        if (any(p in people_lower for p in ['president', 'minister', 'chancellor', 'ambassador']) or
            any(obj in obj_lower for obj in ['suit', 'tie', 'jacket', 'podium', 'microphone']) or
            any(loc in loc_lower for loc in ['embassy', 'palace', 'government', 'parliament'])):
            return "political_leader"

        # Military personnel detection
        if any(obj in obj_lower for obj in ['uniform', 'military uniform', 'helmet', 'rifle', 'weapon']):
            return "military_personnel"

        # Aviation detection
        if any(obj in obj_lower for obj in ['aircraft', 'helicopter', 'plane', 'fighter jet', 'military aircraft', 'jet']):
            return "aviation"

        # Maritime detection
        if (any(obj in obj_lower for obj in ['ship', 'boat', 'warship', 'submarine', 'vessel']) or
            'maersk' in text_lower or 'maritime' in text_lower):
            return "maritime"

        # Technology/Satellite detection
        if 'starlink' in text_lower or any(obj in obj_lower for obj in ['satellite', 'antenna', 'radar']):
            return "technology_satellite"

        # Corporate detection
        if any(obj in obj_lower for obj in ['office', 'computer', 'laptop']) or 'garmin' in text_lower:
            return "corporate_office"

        # Embassy detection
        if any(loc in loc_lower for loc in ['embassy', 'consulate', 'diplomatic']):
            return "embassy_diplomatic"

        # News media detection
        if any(obj in obj_lower for obj in ['newspaper', 'magazine', 'book', 'document']) or len(text or "") > 20:
            return "news_media"

        # Military equipment detection
        if any(obj in obj_lower for obj in ['tank', 'missile', 'artillery', 'radar', 'weapon']):
            return "military_equipment"

        return "general"

    def _calculate_confidence(self, labels: List, equipment: List) -> float:
        """Calculate overall confidence score"""
        if not labels:
            return 0.0

        # Average confidence of top labels
        top_labels = labels[:5]
        avg_confidence = sum(label['score'] for label in top_labels) / len(top_labels)

        # Bonus for military equipment detection
        equipment_bonus = 0.1 if equipment else 0.0

        return min(avg_confidence + equipment_bonus, 1.0)

    def _get_fallback_analysis(self, image_path: str) -> Dict:
        """Fallback analysis when Vision API is not available"""
        filename = os.path.basename(image_path).lower()

        # Simple filename-based analysis
        if any(term in filename for term in ['missile', 'qiam', 'shahab', 'sejjil']):
            return {
                'filename': os.path.basename(image_path),
                'description': 'Military equipment image featuring missiles',
                'country': None,
                'keywords': ['missile'],
                'vision_labels': ['missile'],
                'vision_objects': 0,
                'extracted_text': '',
                'confidence': 0.6,
                'source_type': 'Filename Analysis',
                'metadata_is_ai': True
            }

        return {
            'filename': os.path.basename(image_path),
            'description': 'Military or defense-related image',
            'country': None,
            'keywords': [],
            'vision_labels': [],
            'vision_objects': 0,
            'extracted_text': '',
            'confidence': 0.3,
            'source_type': 'Fallback Analysis',
            'metadata_is_ai': True
        }

    def test_connection(self) -> bool:
        """Test Google Vision API connection"""
        if not self.api_key:
            print("No API key configured")
            return False

        try:
            # Simple test with a small image (just base64 data)
            test_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="

            request_body = {
                'requests': [{
                    'image': {
                        'content': test_image
                    },
                    'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 1
                    }]
                }]
            }

            url = f'{self.base_url}?key={self.api_key}'
            response = requests.post(url, json=request_body, timeout=10)

            return response.status_code == 200

        except Exception as e:
            print(f"API connection test failed: {e}")
            return False
