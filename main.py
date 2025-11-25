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

# Directory containing CSV files
RAW_DATA_DIR = Path("DATA")


def boot_system():
    print("\n" + "=" * 60)
    print("  >> SYSTEM INITIALISATION SEQUENCE STARTED")
    print("=" * 60 + "\n")

    # 1️⃣ Database connection
    if DB_PATH.exists():
        print(f" [*] Existing database found: {DB_PATH.name}")
    else:
        print(f" [*] Creating new database: {DB_PATH.name}")

    conn = connect_database()

    # 2️⃣ Apply schema
    print(" [+] Applying database schema (creating tables if missing)...")
    create_all_tables(conn)

    # 3️⃣ Bulk CSV import with column mapping for cyber_incidents
    print("\n [+] Loading CSV datasets...")

    data_map = {
        "cyber_incidents.csv": ("cyber_incidents", {"incident_type": "category"}),  # map CSV column
        "datasets_metadata.csv": ("datasets_metadata", None),
        "it_tickets.csv": ("it_tickets", None)
    }

    cursor = conn.cursor()

    for csv_name, (table_name, col_map) in data_map.items():
        file_path = RAW_DATA_DIR / csv_name
        if not file_path.exists():
            print(f"[!] CSV not found: {csv_name}")
            continue

        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            existing_rows = cursor.fetchone()[0]
            if existing_rows == 0:
                print(f" -> Loading {csv_name} into '{table_name}'...")
                inserted = load_csv_to_table(file_path, table_name, if_exists="append", column_map=col_map)
                print(f" -> {inserted} rows inserted.")
            else:
                print(f" -> Table '{table_name}' already has {existing_rows} rows. Skipping.")
        except Exception as e:
            print(f"[!] Error processing {csv_name}: {e}")

    # 4️⃣ Admin account provisioning
    print("\n [+] Checking admin account...")
    if not get_user_by_username("admin"):
        success, msg = register_user("admin", "Admin123!", role="admin")
        print(f" -> Admin account created: {msg}")
    else:
        print(" -> Admin account already exists.")

    conn.close()

    # 5️⃣ Completion message
    print("\n" + "=" * 60)
    print("  >> BOOT COMPLETE — SYSTEM READY")
    print("  >> Launch Streamlit interface with:")
    print("       streamlit run Home.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    boot_system()
