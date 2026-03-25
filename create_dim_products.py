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
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dim_products.csv")


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
    product_crm_df = fetch_table_as_df(conn, "SELECT * FROM transformation.crm_prd_info")
    category_erp_df = fetch_table_as_df(conn, "SELECT * FROM transformation.erp_px_cat_g1v2")

    # merge product info with category info
    df = pd.merge(
        left=product_crm_df,
        right=category_erp_df,
        how="left",
        left_on="prd_category",
        right_on="id"
    )

    # build dimension table
    dim_products = pd.DataFrame({
        "product_number": df["prd_key"],
        "product_name": df["prd_nm"],
        "category_id": df["prd_category"],
        "category": df["cat"],
        "subcategory": df["subcat"],
        "maintenance": df["maintenance"],
        "cost": df["prd_cost"],
        "product_line": df["prd_line"],
        "start_date": df["prd_start_dt"],
        "end_date": df["prd_end_dt"]
    })

    # sort and create surrogate key
    dim_products = dim_products.sort_values("product_number").reset_index(drop=True)
    dim_products.insert(0, "product_key", dim_products.index + 1)

    conn.close()

    # create output folder if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # save csv
    dim_products.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned CSV saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
