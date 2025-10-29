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

cursor.execute("SELECT description FROM image_metadata WHERE filename = '16228_000_1WH70V.png'")
result = cursor.fetchone()
print('Current DB description:', result[0] if result else 'Not found')

cursor.close()
conn.close()
