import psycopg

# database connection info
DB_NAME = "DWH"
HOST = "localhost"
PORT = 1974
USER = "postgres"
PASSWORD = "mirzaway"


# cleaned files and their target tables
files_to_load = [
    (
        "transformation.crm_cust_info",
        "datasets/transformed/crm_cust_info_cleaned.csv"
    ),
]


# load cleaned csv into transformation schema
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
        print("all cleaned csv files loaded successfully")

    except Exception as e:
        conn.rollback()
        print("error while loading transformed data:")
        print(e)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
