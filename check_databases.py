#!/usr/bin/env python3
"""
Check all database files to understand what data is already processed
"""

import sqlite3
import json
import os

def check_database(db_path):
    """Check a single database file"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist")
        return

    print(f"\n=== {db_path} ===")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Records: {count}")

            # Show sample data for main tables
            if table_name in ['classifications', 'image_metadata'] and count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                columns = [desc[0] for desc in cursor.description]
                print(f"  Columns: {columns}")

                rows = cursor.fetchall()
                for i, row in enumerate(rows):
                    print(f"  Sample {i+1}: {row[:3]}...")  # Show first 3 columns

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error reading {db_path}: {e}")

def main():
    """Check all database files"""
    databases = ['fast_classification.db', 'image_classification.db', 'image_metadata.db']

    for db_path in databases:
        check_database(db_path)

    print("\n=== SUMMARY ===")
    print("To preserve existing work, we'll:")
    print("1. Read existing classifications from SQLite databases")
    print("2. Create a new Google Vision-based classifier")
    print("3. Only process NEW images not already in the database")
    print("4. Use Google Vision for better accuracy on new images")

if __name__ == "__main__":
    main()
