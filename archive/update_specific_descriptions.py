#!/usr/bin/env python3
"""
Update specific image descriptions in the database with manually provided better descriptions
"""
import psycopg2

def update_specific_descriptions():
    """Update specific images with manually curated descriptions"""

    # Manual description updates
    updates = [
        {
            'filename': '000EA_36MQ9WH.png',
            'description': "SpaceX's Starship erected on a launch pad."
        },
        {
            'filename': '000EW_shutterstock_715210177.png',
            'description': "Artist's rendering of a missile or ICBM in flight above the clouds."
        },
        {
            'filename': '000E6_1KW5RY.png',
            'description': "Chinese military parade with vehicles or TELs displaying the DF-71 Chinese solid-fueled road-mobile medium-range ballistic missile."
        },
        {
            'filename': '000B2_051_XxjpbeE007032_20191217_PEPFN0A001.png',
            'description': "A Long March-3A carrier rocket carrying two satellites of the Beidou Navigation Satellite System blasts off from Xichang Satellite Launch Center in Xichang, China's Sichuan Province, on December 16, 2019. Photo: Xinhua."
        },
        {
            'filename': '000BY_shutterstock_413774935.png',
            'description': "SAMARA, RUSSIA - JUNE 2: Real 'Soyuz' type rocket as monument on June 2, 2012 in Samara. Rocket height together with building - 68 meters, weight - 20 tons. The monument was unveiled on 2001."
        }
    ]

    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        database='image_classification',
        user='postgres',
        password='class123',
        port=5433
    )
    cursor = conn.cursor()

    updated_count = 0

    for update in updates:
        try:
            # Update the description
            cursor.execute("""
            UPDATE image_metadata
            SET description = %s, processed_at = NOW()
            WHERE filename = %s
            """, (update['description'], update['filename']))

            if cursor.rowcount > 0:
                print(f"[UPDATED] {update['filename']}")
                print(f"  New description: {update['description'][:80]}...")
                updated_count += 1
            else:
                print(f"[NOT FOUND] {update['filename']}")

        except Exception as e:
            print(f"[ERROR] updating {update['filename']}: {e}")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print(f"\nCompleted: {updated_count}/{len(updates)} images updated successfully")

if __name__ == "__main__":
    update_specific_descriptions()
