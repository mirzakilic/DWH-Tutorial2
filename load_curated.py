import psycopg

# -----------------------------
# CONNECTION SETTINGS
# -----------------------------
DB_NAME = "DWH"
HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "seymen123"


# -----------------------------
# FILE PATHS + TABLES
# -----------------------------
files_to_load = [
    (
        "curated.dim_customers",
        r"C:\Users\seyme\OneDrive\Masaüstü\Data engineering and Data governance\curated_dim_customers.csv"
    ),
    (
        "curated.dim_products",
        r"C:\Users\seyme\OneDrive\Masaüstü\Data engineering and Data governance\curated_dim_products.csv"
    ),
    (
        "curated.fact_sales",
        r"C:\Users\seyme\OneDrive\Masaüstü\Data engineering and Data governance\curated_fact_sales.csv"
    ),
]


# -----------------------------
# LOAD DATA
# -----------------------------
def main():
    conn = psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
    )

    try:
        with conn.cursor() as cur:
            for table_name, file_path in files_to_load:
                with cur.copy(f"""
                    COPY {table_name}
                    FROM STDIN
                    WITH (FORMAT csv, HEADER true)
                """) as copy:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            copy.write(line)

                print(f"✅ {table_name} loaded from {file_path}")

        conn.commit()
        print("🎉 All CSV files loaded successfully")

    except Exception as e:
        conn.rollback()
        print("❌ Error while loading data:")
        print(e)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
