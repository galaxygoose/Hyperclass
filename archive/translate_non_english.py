#!/usr/bin/env python3
"""
Identify and translate non-English descriptions in the database
"""
import psycopg2
import re

def detect_language(text):
    """Simple language detection based on character sets and common patterns"""
    if not text or not isinstance(text, str):
        return 'unknown'

    text_lower = text.lower().strip()

    # Cyrillic (Russian, Ukrainian, etc.) - check for significant Cyrillic content
    cyrillic_chars = sum(1 for char in text if ord(char) in range(0x0400, 0x04FF))
    if cyrillic_chars > len(text) * 0.5:  # Must be majority Cyrillic
        return 'russian'

    # Arabic - check for significant Arabic content
    arabic_chars = sum(1 for char in text if ord(char) in range(0x0600, 0x06FF))
    if arabic_chars > len(text) * 0.5:  # Must be majority Arabic
        return 'arabic'

    # Chinese/Japanese/Korean - check for significant CJK content
    cjk_chars = sum(1 for char in text if ord(char) in range(0x4E00, 0x9FFF) or
                   ord(char) in range(0x3040, 0x309F) or
                   ord(char) in range(0xAC00, 0xD7AF))
    if cjk_chars > len(text) * 0.5:  # Must be majority CJK
        return 'cjk'

    # Check for non-Latin scripts that are clearly foreign
    non_latin_chars = sum(1 for char in text if ord(char) > 127)
    if non_latin_chars > len(text) * 0.8:  # Overwhelmingly non-Latin
        if cyrillic_chars > arabic_chars and cyrillic_chars > cjk_chars:
            return 'russian'
        elif arabic_chars > cjk_chars:
            return 'arabic'
        else:
            return 'cjk'

    # For Latin-script text, be very conservative about language detection
    # Only flag as non-English if we find definitive foreign language patterns

    words = text_lower.split()

    # Spanish detection - require multiple Spanish words
    spanish_indicators = ['el', 'la', 'los', 'las', 'un', 'una', 'es', 'son', 'está', 'están']
    spanish_count = sum(1 for word in words if word in spanish_indicators)
    if spanish_count >= 2 and len(words) <= 10:  # Multiple Spanish words in short text
        return 'spanish'

    # French detection - require multiple French words
    french_indicators = ['le', 'la', 'les', 'et', 'à', 'de', 'du', 'des', 'pour', 'dans', 'sur']
    french_count = sum(1 for word in words if word in french_indicators)
    if french_count >= 2 and len(words) <= 10:  # Multiple French words in short text
        return 'french'

    # German detection - require multiple German words
    german_indicators = ['der', 'die', 'das', 'und', 'in', 'von', 'zu', 'mit', 'ist', 'auf']
    german_count = sum(1 for word in words if word in german_indicators)
    if german_count >= 2 and len(words) <= 10:  # Multiple German words in short text
        return 'german'

    # Default to English for Latin-script text
    return 'english'

def translate_to_english(text, detected_lang):
    """Translate text to English using simple rule-based translations for common cases"""
    if detected_lang == 'english':
        return text

    # For now, we'll implement basic translations for common military/news terms
    # In a production system, you'd use Google Translate API or similar

    translations = {
        'russian': {
            'подлодка': 'submarine',
            'ракета': 'missile',
            'самолет': 'aircraft',
            'корабль': 'ship',
            'войска': 'troops',
            'армия': 'army',
            'военный': 'military'
        },
        'arabic': {
            'صاروخ': 'missile',
            'طائرة': 'aircraft',
            'سفينة': 'ship',
            'جيش': 'army',
            'عسكري': 'military'
        },
        'spanish': {
            'misil': 'missile',
            'avión': 'aircraft',
            'barco': 'ship',
            'ejército': 'army',
            'militar': 'military',
            'parada': 'parade'
        }
    }

    if detected_lang in translations:
        translated_text = text
        for foreign_word, english_word in translations[detected_lang].items():
            translated_text = re.sub(r'\b' + re.escape(foreign_word) + r'\b', english_word, translated_text, flags=re.IGNORECASE)

        # If we made changes, mark as translated
        if translated_text != text:
            return f"[Translated from {detected_lang.title()}]: {translated_text}"

    # For languages we can't translate automatically, mark for manual translation
    return f"[NEEDS TRANSLATION FROM {detected_lang.upper()}]: {text}"

def find_and_translate_non_english():
    """Find non-English descriptions and translate them"""

    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        database='image_classification',
        user='postgres',
        password='class123',
        port=5433
    )
    cursor = conn.cursor()

    # Get all descriptions
    cursor.execute("SELECT id, filename, description FROM image_metadata WHERE description IS NOT NULL AND description != ''")
    rows = cursor.fetchall()

    print(f"Checking {len(rows)} descriptions for non-English content...")

    updated_count = 0
    non_english_found = []

    for row_id, filename, description in rows:
        detected_lang = detect_language(description)

        if detected_lang != 'english':
            print(f"\n[NON-ENGLISH] detected in {filename}")
            print(f"   Language: {detected_lang}")
            print(f"   Original: {description[:100]}...")

            # Translate to English
            translated = translate_to_english(description, detected_lang)
            print(f"   Translated: {translated[:100]}...")

            # Update the database
            try:
                cursor.execute("""
                UPDATE image_metadata
                SET description = %s, processed_at = NOW()
                WHERE id = %s
                """, (translated, row_id))

                updated_count += 1
                non_english_found.append((filename, detected_lang, description[:50], translated[:50]))

            except Exception as e:
                print(f"   ❌ Error updating: {e}")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Completed: {updated_count} non-English descriptions translated")

    if non_english_found:
        print("\n📋 Summary of translations:")
        for filename, lang, orig, trans in non_english_found[:10]:  # Show first 10
            print(f"  {filename}: {lang} → {trans}...")

        if len(non_english_found) > 10:
            print(f"  ... and {len(non_english_found) - 10} more")

if __name__ == "__main__":
    find_and_translate_non_english()
