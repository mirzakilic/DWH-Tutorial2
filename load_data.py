import psycopg

# database connection info
DB_NAME = "DWH"
HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "mirzakilic"


# csv files and their target tables
files_to_load = [
    (
        "ingestion.crm_cust_info",
        "datasets/source_crm/cust_info.csv"
    ),
    (
        "ingestion.crm_prd_info",
        "datasets/source_crm/prd_info.csv"
    ),
    (
        "ingestion.crm_sales_details",
        "datasets/source_crm/sales_details.csv"
    ),
    (
        "ingestion.erp_cust_az12",
        "datasets/source_erp/CUST_AZ12.csv"
    ),
    (
        "ingestion.erp_loc_a101",
        "datasets/source_erp/LOC_A101.csv"
    ),
    (
        "ingestion.erp_px_cat_g1v2",
        "datasets/source_erp/PX_CAT_G1V2.csv"
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

                print(f"loaded {table_name} from {file_path}")

        conn.commit()
        print("all csv files loaded successfully")

    except Exception as e:
        conn.rollback()
        print("error while loading data:")
        print(e)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
