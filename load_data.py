import psycopg

# database connection info
DB_NAME = "DWH"
HOST = "localhost"
PORT = 1974
USER = "postgres"
PASSWORD = "mirzaway"


# csv files and their target tables
files_to_load = [
    (
        "ingestion.crm_cust_info",
        r"/Users/mirzakilic/Downloads\datasets\source_crm\cust_info.csv"
    ),
    (
        "ingestion.crm_prd_info",
        r"/Users/mirzakilic/Downloads\datasets\source_crm\prd_info.csv"
    ),
    (
        "ingestion.crm_sales_details",
        r"/Users/mirzakilic/Downloads\datasets\source_crm\sales_details.csv"
    ),
    (
        "ingestion.erp_cust_az12",
       r"/Users/mirzakilic/Downloads\datasets\source_erp\CUST_AZ12.csv"
    ),
    (
        "ingestion.erp_loc_a101",
        r"/Users/mirzakilic/Downloads\datasets\source_erp\LOC_A101.csv"
    ),
    (
        "ingestion.erp_px_cat_g1v2",
        r"/Users/mirzakilic/Downloads\datasets\source_erp\PX_CAT_G1V2.csv"
    ),
]


# main loading logic
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
