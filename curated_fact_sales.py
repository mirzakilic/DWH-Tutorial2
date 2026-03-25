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
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "fact_sales.csv")


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

    # read tables
    sales_detail_df = fetch_table_as_df(conn, "SELECT * FROM transformation.crm_sales_details")
    dim_products_df = fetch_table_as_df(conn, "SELECT * FROM curated.dim_products")
    dim_customers_df = fetch_table_as_df(conn, "SELECT * FROM curated.dim_customers")

    # merge with product dimension
    df = pd.merge(
        left=sales_detail_df,
        right=dim_products_df[["product_key", "product_number"]],
        how="left",
        left_on="sls_prd_key",
        right_on="product_number"
    )

    # merge with customer dimension
    df = pd.merge(
        left=df,
        right=dim_customers_df[["customer_key", "customer_id"]],
        how="left",
        left_on="sls_cust_id",
        right_on="customer_id"
    )

    # create fact table
    fact_sales = pd.DataFrame({
        "product_key": df["product_key"],
        "customer_key": df["customer_key"],
        "order_number": df["sls_ord_num"],
        "order_date": df["sls_order_dt"],
        "shipping_date": df["sls_ship_dt"],
        "due_date": df["sls_due_dt"],
        "sales": df["sls_sales"],
        "quantity": df["sls_quantity"],
        "price": df["sls_price"]
    })

    # create surrogate key
    fact_sales = fact_sales.reset_index(drop=True)
    fact_sales.insert(0, "sales_key", fact_sales.index + 1)

    conn.close()

    # make output folder if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # save csv
    fact_sales.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned CSV saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
