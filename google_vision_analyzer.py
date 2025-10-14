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

        # Generate comprehensive description for news/media searchability
        description = self._generate_news_description(
            detected_people, detected_locations, detected_organizations,
            detected_objects, detected_countries, extracted_text
        )

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

            # Very high confidence threshold and strict military equipment-only filtering
            if confidence > 0.85:  # Only very confident detections
                # Only include labels that are clearly actual military equipment (not flags or locations)
                if any(equipment_term in label_desc for equipment_term in [
                    'tank', 'missile', 'aircraft', 'helicopter', 'warship', 'submarine',
                    'armored vehicle', 'fighter jet', 'military aircraft', 'combat aircraft',
                    'weapon', 'military vehicle'
                ]) and not any(env_term in label_desc for env_term in [
                    'flag', 'pole', 'sunlight', 'wind', 'day', 'government', 'blue',
                    'person', 'people', 'crowd', 'united states', 'america', 'country', 'flag of'  # Exclude flags and locations
                ]):
                    # Use Vision API's specific military equipment label
                    equipment.append(label['description'])
                # Also catch very specific military equipment labels (but not flags or locations)
                elif ('military' in label_desc or 'combat' in label_desc) and confidence > 0.9 and 'flag' not in label_desc:
                    equipment.append(label['description'])

        # Process localized objects for specific military equipment
        for obj in objects:
            obj_name = obj['name'].lower()
            confidence = obj['score']

            if confidence > 0.75:  # Higher threshold for objects
                if any(equipment_term in obj_name for equipment_term in [
                    'tank', 'missile', 'aircraft', 'helicopter', 'warship', 'armored vehicle', 'weapon', 'military vehicle'
                ]) and obj_name not in ['flag', 'person', 'people']:  # Exclude flags and people as they're not equipment
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

            if confidence > 0.7:  # Moderate threshold for people detection
                # Look for specific people, politicians, leaders, officials
                if any(person_term in label_desc for person_term in [
                    'president', 'prime minister', 'minister', 'secretary', 'ambassador',
                    'governor', 'mayor', 'senator', 'congressman', 'diplomat',
                    'politician', 'leader', 'official', 'spokesperson', 'businessperson',
                    'executive', 'director', 'chairman', 'ceo', 'founder'
                ]) and not any(generic_term in label_desc for generic_term in [
                    'person', 'people', 'man', 'woman', 'crowd', 'group', 'audience', 'citizen'
                ]):
                    people.append(label['description'])

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

    def _generate_news_description(self, people: List, locations: List, organizations: List,
                                 objects: List, countries: List, text: str) -> str:
        """Generate comprehensive news/media description for searchability"""

        # Create more descriptive and contextual descriptions for news/media

        # Primary: People + Location + Context
        if people and locations and organizations:
            person = people[0]
            location = locations[0]
            org = organizations[0]
            return f"{person} at {org} {location}"

        elif people and locations:
            person = people[0]
            location = locations[0]
            if countries:
                return f"{person} at {location} in {countries[0]}"
            else:
                return f"{person} at {location}"

        elif people and organizations:
            person = people[0]
            org = organizations[0]
            return f"{person} representing {org}"

        elif locations and organizations:
            location = locations[0]
            org = organizations[0]
            if countries:
                return f"{org} {location} in {countries[0]}"
            else:
                return f"{org} {location}"

        elif people:
            # Use specific people detected by Vision API
            if len(people) > 1:
                # Multiple specific people
                primary_person = people[0]
                secondary_person = people[1]

                # Check if these are specific names vs generic roles
                if (primary_person.lower() not in ['person', 'people', 'man', 'woman', 'official', 'spokesperson'] and
                    secondary_person.lower() not in ['person', 'people', 'man', 'woman', 'official', 'spokesperson']):
                    return f"{primary_person} and {secondary_person} at official event"
                else:
                    return "Government officials and representatives"
            else:
                # Single person
                person = people[0]
                # Use specific name if it's not a generic term
                if person.lower() not in ['person', 'people', 'man', 'woman', 'official', 'spokesperson', 'businessperson']:
                    return f"{person} in official capacity"
                else:
                    return "Government official in public capacity"

        elif locations:
            # Specific buildings/locations with context
            location = locations[0]
            if 'embassy' in location.lower():
                if countries:
                    return f"{countries[0]} embassy diplomatic facility"
                else:
                    return f"Diplomatic embassy facility"
            elif 'headquarters' in location.lower() or 'office' in location.lower():
                return f"Corporate headquarters and office complex"
            elif 'building' in location.lower():
                return f"Commercial building and business facility"
            else:
                return f"{location} facility and operations"

        elif organizations:
            # Organizations with their activities
            org = organizations[0]
            if 'military' in org.lower():
                return f"Military organization operations and activities"
            elif 'government' in org.lower():
                return f"Government agency operations and services"
            elif 'huawei' in org.lower() or 'company' in org.lower():
                return f"Corporate operations and business activities"
            else:
                return f"{org} institutional operations"

        elif objects and countries:
            # Only use objects as equipment if they're actually equipment, not symbols
            primary_obj = objects[0]
            obj_lower = primary_obj.lower()

            # Check if this object is actually equipment, not a symbol or generic item
            if any(equipment_term in obj_lower for equipment_term in [
                'tank', 'missile', 'aircraft', 'helicopter', 'warship', 'vehicle', 'weapon'
            ]) and obj_lower not in ['flag', 'person', 'people']:
                return f"{countries[0]} {primary_obj} in operational use"
            else:
                # For non-equipment objects, use a more generic description
                return f"{countries[0]} facilities and operations"

        elif objects:
            # Equipment/objects with specific context - only for actual equipment
            primary_obj = objects[0]
            obj_lower = primary_obj.lower()

            # Check if this object is actually equipment
            if any(equipment_term in obj_lower for equipment_term in [
                'tank', 'missile', 'aircraft', 'helicopter', 'warship', 'vehicle', 'weapon'
            ]) and obj_lower not in ['flag', 'person', 'people']:
                if any(term in obj_lower for term in ['aircraft', 'helicopter', 'plane']):
                    return f"Aviation and aircraft operations"
                elif any(term in obj_lower for term in ['vehicle', 'tank', 'armored']):
                    return f"Military and defense vehicle operations"
                else:
                    return f"Military equipment operations"
            elif obj_lower == 'flag' and countries:
                return f"{countries[0]} national symbols and flags"
            elif obj_lower == 'flag':
                return f"National flags and official symbols"
            else:
                return f"Operations and facility usage"

        elif text:
            # OCR text provides specific context
            if any(military_term in text.upper() for military_term in ['TEL', 'SAM', 'ICBM', 'USS', 'HMS']):
                return f"Military equipment with designation '{text}'"
            elif len(text) > 3:
                return f"Content featuring text '{text}'"
            else:
                return f"Documented content and records"

        elif countries:
            return f"National operations and activities in {countries[0]}"

        else:
            return "News, media, and public information content"

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
