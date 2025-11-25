import pandas as pd
from app.data.db import connect_database

def load_dataset_row(dataset_name, category, source, last_updated, record_count, file_size_mb):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

def get_all_datasets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    conn.close()
    return df

# -----------------------------
# Robust CSV loader
# -----------------------------
def load_csv_to_table(csv_path, table_name, if_exists="append", column_map=None):
    """
    Loads CSV into DB, optionally mapping columns to match DB table.
    Ignores extra CSV columns.
    """
    try:
        df = pd.read_csv(csv_path)
        conn = connect_database()

        # Auto map CSV headers to DB if column_map provided
        if column_map:
            df = df.rename(columns=column_map)

        # Get DB columns
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        table_columns = [col[1] for col in cursor.fetchall()]
        df = df[[c for c in df.columns if c in table_columns]]  # keep only existing DB columns

        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.close()
        return len(df)

    except Exception as e:
        print(f"[!] Error importing {csv_path}: {e}")
        return 0
