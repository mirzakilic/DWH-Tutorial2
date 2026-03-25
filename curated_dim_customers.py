import os
import psycopg
import pandas as pd

DB_NAME = "DWH"
HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "mirzakilic"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "datasets", "curated")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dim_customers.csv")


def fetch_table_as_df(conn, query):
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=cols)


def main():
    conn = psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        autocommit=True
    )

    # read tables from transformation schema
    customer_crm_df = fetch_table_as_df(conn, "SELECT * FROM transformation.crm_cust_info")
    customer_erp_df = fetch_table_as_df(conn, "SELECT * FROM transformation.erp_cust_az12")
    location_erp_df = fetch_table_as_df(conn, "SELECT * FROM transformation.erp_loc_a101")

    # merge crm with erp customer
    df = pd.merge(
        left=customer_crm_df,
        right=customer_erp_df,
        how="left",
        left_on="cst_key",
        right_on="cid"
    )

    # merge with erp location
    df = pd.merge(
        left=df,
        right=location_erp_df,
        how="left",
        left_on="cst_key",
        right_on="cid",
        suffixes=("", "_loc")
    )

    # build dimension table
    dim_customers = pd.DataFrame({
        "customer_id": df["cst_id"],
        "customer_number": df["cst_key"],
        "first_name": df["cst_firstname"],
        "last_name": df["cst_lastname"],
        "country": df["cntry"],
        "marital_status": df["cst_marital_status"],
        "gender": df["cst_gndr"],
        "birthdate": df["bdate"],
        "create_date": df["cst_create_date"]
    })

    # sort and create surrogate key
    dim_customers = dim_customers.sort_values("customer_id").reset_index(drop=True)
    dim_customers.insert(0, "customer_key", dim_customers.index + 1)

    conn.close()

    # create output folder if it does not exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # save csv
    dim_customers.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned CSV saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
