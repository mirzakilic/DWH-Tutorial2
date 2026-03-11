import psycopg

# database connection settings
DB_NAME = "DWH"
HOST = "localhost"
PORT = 1974
USER = "postgres"
PASSWORD = "mirzaway"

# schema for transformed tables
TRANSFORMATION_SCHEMA = "transformation"


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
            # create the transformation schema if needed
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {TRANSFORMATION_SCHEMA};")

            # remove old versions so the script can be rerun cleanly
            cur.execute(f"DROP TABLE IF EXISTS {TRANSFORMATION_SCHEMA}.fact_sales;")
            cur.execute(f"DROP TABLE IF EXISTS {TRANSFORMATION_SCHEMA}.dim_customers;")
            cur.execute(f"DROP TABLE IF EXISTS {TRANSFORMATION_SCHEMA}.dim_products;")

            # -------------------------
            # customer transformation
            # -------------------------
            cur.execute(f"""
                CREATE TABLE {TRANSFORMATION_SCHEMA}.dim_customers AS
                WITH crm_customers_dedup AS (
                    SELECT
                        cst_id,
                        cst_key,
                        cst_firstname,
                        cst_lastname,
                        cst_marital_status,
                        cst_gndr,
                        cst_create_date,
                        ROW_NUMBER() OVER (
                            PARTITION BY cst_id
                            ORDER BY cst_create_date DESC NULLS LAST
                        ) AS rn
                    FROM ingestion.crm_cust_info
                    WHERE cst_id IS NOT NULL
                )
                SELECT
                    c.cst_id AS customer_id,
                    c.cst_key AS customer_key,
                    c.cst_firstname AS first_name,
                    c.cst_lastname AS last_name,
                    COALESCE(c.cst_marital_status, 'Unknown') AS marital_status,
                    CASE
                        WHEN UPPER(TRIM(COALESCE(c.cst_gndr, e.gen))) IN ('M', 'MALE') THEN 'Male'
                        WHEN UPPER(TRIM(COALESCE(c.cst_gndr, e.gen))) IN ('F', 'FEMALE') THEN 'Female'
                        ELSE 'Unknown'
                    END AS gender,
                    CASE
                        WHEN e.bdate IS NULL OR TRIM(e.bdate) = '' THEN NULL
                        ELSE e.bdate::date
                    END AS birth_date,
                    CASE
                        WHEN l.cntry IS NULL OR TRIM(l.cntry) = '' THEN 'Unknown'
                        WHEN UPPER(TRIM(l.cntry)) IN ('US', 'USA', 'UNITED STATES') THEN 'United States'
                        WHEN UPPER(TRIM(l.cntry)) IN ('DE', 'GERMANY') THEN 'Germany'
                        ELSE TRIM(l.cntry)
                    END AS country,
                    c.cst_create_date AS create_date,
                    CASE
                        WHEN e.bdate IS NULL OR TRIM(e.bdate) = '' THEN NULL
                        ELSE EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.bdate::date))
                    END AS age,
                    CASE
                        WHEN e.bdate IS NULL OR TRIM(e.bdate) = '' THEN 'Unknown'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.bdate::date)) < 30 THEN 'Under 30'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.bdate::date)) BETWEEN 30 AND 49 THEN '30-49'
                        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.bdate::date)) >= 50 THEN '50+'
                        ELSE 'Unknown'
                    END AS age_group
                FROM crm_customers_dedup c
                LEFT JOIN ingestion.erp_cust_az12 e
                    ON 'NAS' || c.cst_key = e.cid
                LEFT JOIN ingestion.erp_loc_a101 l
                    ON substring(c.cst_key from 1 for 2) || '-' || substring(c.cst_key from 3) = l.cid
                WHERE c.rn = 1;
            """)

            # -------------------------
            # product transformation
            # -------------------------
            cur.execute(f"""
                CREATE TABLE {TRANSFORMATION_SCHEMA}.dim_products AS
                WITH crm_products_dedup AS (
                    SELECT
                        prd_id,
                        prd_key,
                        prd_nm,
                        prd_cost,
                        TRIM(prd_line) AS prd_line,
                        prd_start_dt,
                        prd_end_dt,
                        ROW_NUMBER() OVER (
                            PARTITION BY prd_key
                            ORDER BY
                                CASE WHEN prd_end_dt IS NULL THEN 0 ELSE 1 END,
                                prd_start_dt DESC NULLS LAST
                        ) AS rn
                    FROM ingestion.crm_prd_info
                    WHERE prd_key IS NOT NULL
                )
                SELECT
                    p.prd_id AS product_id,
                    p.prd_key AS product_key,
                    p.prd_nm AS product_name,
                    p.prd_cost AS product_cost,
                    p.prd_line AS product_line,
                    e.id AS category_id,
                    e.cat AS category,
                    e.subcat AS subcategory,
                    e.maintenance AS maintenance,
                    p.prd_start_dt AS start_date,
                    p.prd_end_dt AS end_date
                FROM crm_products_dedup p
                LEFT JOIN ingestion.erp_px_cat_g1v2 e
                    ON REPLACE(SUBSTRING(p.prd_key FROM 1 FOR 5), '-', '_') = e.id
                WHERE p.rn = 1;
            """)

            # -------------------------
            # sales transformation
            # -------------------------
            cur.execute(f"""
                CREATE TABLE {TRANSFORMATION_SCHEMA}.fact_sales AS
                SELECT
                    sls_ord_num AS order_number,
                    sls_prd_key AS product_key,
                    sls_cust_id AS customer_id,
                    CASE
                        WHEN sls_order_dt IS NULL OR TRIM(sls_order_dt) = '' OR sls_order_dt = '0' THEN NULL
                        ELSE TO_DATE(sls_order_dt, 'YYYYMMDD')
                    END AS order_date,
                    CASE
                        WHEN sls_ship_dt IS NULL OR TRIM(sls_ship_dt) = '' OR sls_ship_dt = '0' THEN NULL
                        ELSE TO_DATE(sls_ship_dt, 'YYYYMMDD')
                    END AS ship_date,
                    CASE
                        WHEN sls_due_dt IS NULL OR TRIM(sls_due_dt) = '' OR sls_due_dt = '0' THEN NULL
                        ELSE TO_DATE(sls_due_dt, 'YYYYMMDD')
                    END AS due_date,
                    sls_sales AS sales_amount,
                    sls_quantity AS quantity_sold,
                    sls_price AS unit_price,
                    CASE
                        WHEN sls_order_dt IS NULL OR TRIM(sls_order_dt) = '' OR sls_order_dt = '0'
                             OR sls_ship_dt IS NULL OR TRIM(sls_ship_dt) = '' OR sls_ship_dt = '0'
                        THEN NULL
                        ELSE TO_DATE(sls_ship_dt, 'YYYYMMDD') - TO_DATE(sls_order_dt, 'YYYYMMDD')
                    END AS fulfillment_days
                FROM ingestion.crm_sales_details;
            """)

        conn.commit()
        print("transformation tables created successfully")

    except Exception as e:
        conn.rollback()
        print("error while creating transformation tables")
        print(e)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
