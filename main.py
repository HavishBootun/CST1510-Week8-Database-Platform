"""
System Boot Script
------------------
Initialises the SQLite database, applies schema definitions,
loads CSV datasets, and provisions an admin account.

Usage:
    python main.py
"""

from pathlib import Path
from app.data.db import connect_database, DB_PATH
from app.data.schema import create_all_tables
from app.services.user_service import register_user
from app.data.users import get_user_by_username
from app.data.datasets import load_csv_to_table


# Directory containing all raw CSV inputs
RAW_DATA_DIR = Path("DATA")


def boot_system():
    print("\n" + "=" * 60)
    print("  >> SYSTEM INITIALISATION SEQUENCE STARTED")
    print("=" * 60 + "\n")

    # -----------------------------------------
    # 1. Database Connection
    # -----------------------------------------
    if DB_PATH.exists():
        print(f" [*] Existing database detected: {DB_PATH.name}")
    else:
        print(f" [*] Creating new database at: {DB_PATH.name}")

    conn = connect_database()

    # -----------------------------------------
    # 2. Apply Schema Definitions
    # -----------------------------------------
    print(" [+] Creating required tables...")
    create_all_tables(conn)

    # -----------------------------------------
    # 3. Bulk CSV Data Import
    # -----------------------------------------
    print("\n [+] Processing CSV Data Imports...")

    # Map CSV filenames to SQL table names
    data_map = {
        "cyber_incidents.csv": "cyber_incidents",
        "datasets_metadata.csv": "datasets_metadata",
        "it_tickets.csv": "it_tickets"
    }

    cursor = conn.cursor()

    for csv_name, table_name in data_map.items():
        file_path = RAW_DATA_DIR / csv_name

        if not file_path.exists():
            print(f"     [!] WARNING: CSV not found: {csv_name}")
            continue

        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            existing_rows = cursor.fetchone()[0]

            if existing_rows == 0:
                inserted = load_csv_to_table(file_path, table_name, if_exists="append")
                print(f"     -> Loaded {inserted} records into '{table_name}'.")
            else:
                print(f"     -> '{table_name}' already contains {existing_rows} rows. Skipping import.")

        except Exception as err:
            print(f"     [!] ERROR loading {csv_name}: {err}")

    # -----------------------------------------
    # 4. Admin Account Provisioning
    # -----------------------------------------
    print("\n [+] Verifying admin credentials...")

    if not get_user_by_username("admin"):
        success, msg = register_user("admin", "Admin123!", role="admin")
        print(f"     -> Admin account created: {msg}")
    else:
        print("     -> Admin account already exists.")

    conn.close()

    # -----------------------------------------
    # 5. Completion Message
    # -----------------------------------------
    print("\n" + "=" * 60)
    print("  >> BOOT COMPLETE — System Ready.")
    print("  >> Launch the interface using:")
    print("       streamlit run Home.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    boot_system()
