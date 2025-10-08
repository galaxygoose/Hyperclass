#!/usr/bin/env python3
"""
Check the classification results in the database
"""

import sqlite3

def check_database(db_path="fast_classification.db"):
    """Check what's in the database"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM classifications")
    total_count = cursor.fetchone()[0]
    print(f"Database contains {total_count} classified images")

    # Get country breakdown
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

    # Get equipment breakdown
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

    # Show sample results
    cursor.execute("""
    SELECT filename, description, country
    FROM classifications
    WHERE country IS NOT NULL
    LIMIT 5
    """)

    print("\nSAMPLE CLASSIFICATIONS:")
    for filename, description, country in cursor.fetchall():
        print(f"File: {filename[:30]}...")
        print(f"  Description: {description[:50]}...")
        print(f"  Country: {country}")
        print()

    conn.close()

if __name__ == "__main__":
    check_database()

