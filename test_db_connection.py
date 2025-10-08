import psycopg2

def test_database_connection():
    """Test PostgreSQL database connection"""

    # Database connection parameters - update these for your setup
    # Try different connection methods
    connection_attempts = [
        {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': '',
            'port': 5432
        },
        {
            'host': '',
            'database': 'postgres',
            'user': 'postgres',
            'password': '',
            'port': 5432
        },
        {
            'database': 'postgres',
            'user': 'postgres',
            'password': '',
        }
    ]

    for i, db_params in enumerate(connection_attempts):
        try:
            print(f"\nTesting connection method {i+1}...")
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Test query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] Connected to PostgreSQL: {version[0][:50]}...")

            # Check if our database exists
            cursor.execute("SELECT datname FROM pg_database WHERE datname = 'image_classification';")
            db_exists = cursor.fetchone() is not None

            if not db_exists:
                print("Database 'image_classification' does not exist. Creating...")
                conn.autocommit = True
                cursor.execute("CREATE DATABASE image_classification;")
                print("[OK] Database created!")
            else:
                print("[OK] Database 'image_classification' exists")

            # Switch to our database
            cursor.close()
            conn.close()

            db_params['database'] = 'image_classification'
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Check if our table exists
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'image_metadata'
            );
            """)
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("[OK] Table 'image_metadata' exists")

                # Check number of records
                cursor.execute("SELECT COUNT(*) FROM image_metadata;")
                count = cursor.fetchone()[0]
                print(f"[OK] Table contains {count} records")
            else:
                print("[ERROR] Table 'image_metadata' does not exist. Run setup_database.py first.")

            cursor.close()
            conn.close()
            print("[OK] Database connection test successful!")
            return  # Success, exit function

        except psycopg2.OperationalError as e:
            print(f"[ERROR] Connection method {i+1} failed: {e}")
            continue
        except Exception as e:
            print(f"[ERROR] Unexpected error with method {i+1}: {e}")
            continue

    # If we get here, all connection methods failed
    print("\n[ERROR] All connection methods failed!")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Open pgAdmin 4 and verify you can connect")
    print("3. Check PostgreSQL configuration files (postgresql.conf, pg_hba.conf)")
    print("4. Try running PostgreSQL as administrator")
    print("5. Check Windows Firewall settings")

if __name__ == "__main__":
    test_database_connection()
