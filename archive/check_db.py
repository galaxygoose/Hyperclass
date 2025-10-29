#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='image_classification',
    user='postgres',
    password='class123',
    port=5433
)
cursor = conn.cursor()

cursor.execute("SELECT filename, description FROM image_metadata WHERE description LIKE '%Scene featuring%' LIMIT 10")
results = cursor.fetchall()

print(f'Found {len(results)} descriptions with "Scene featuring"')
for filename, desc in results:
    print(f'{filename}: {desc}')

cursor.close()
conn.close()
