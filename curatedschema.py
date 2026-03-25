import psycopg
from psycopg import sql

# -----------------------------
# CONNECTION SETTINGS
# -----------------------------
DB_NAME = "DWH"
SCHEMA_NAME = "curated"
HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "mirzakilic"


# -----------------------------
# CREATE SCHEMA + TABLES
# -----------------------------
def create_schema_and_tables():
    conn = psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        autocommit=True
    )

    try:
        with conn.cursor() as cur:
            # create schema
            cur.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(SCHEMA_NAME)
                )
            )

            # dim_customers
            cur.execute("""
                CREATE TABLE IF NOT EXISTS curated.dim_customers (
                    customer_key INT,
                    customer_id INT,
                    customer_number VARCHAR(20),
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    country VARCHAR(50),
                    marital_status VARCHAR(20),
                    gender VARCHAR(20),
                    birthdate DATE,
                    create_date DATE
                );
            """)

            # dim_products
            cur.execute("""
                CREATE TABLE IF NOT EXISTS curated.dim_products (
                    product_key INT,
                    product_number VARCHAR(50),
                    product_name VARCHAR(100),
                    category_id VARCHAR(20),
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    maintenance VARCHAR(20),
                    cost DECIMAL(10,2),
                    product_line VARCHAR(20),
                    start_date DATE,
                    end_date DATE
                );
            """)

            # fact_sales
            cur.execute("""
                CREATE TABLE IF NOT EXISTS curated.fact_sales (
                    sales_key INT,
                    product_key INT,
                    customer_key INT,
                    order_number VARCHAR(50),
                    order_date DATE,
                    shipping_date DATE,
                    due_date DATE,
                    sales DECIMAL(10,2),
                    quantity INT,
                    price DECIMAL(10,2)
                );
            """)

        print(f"Schema '{SCHEMA_NAME}' and all 3 tables created successfully")

    except Exception as e:
        print("Error while creating schema/tables:")
        print(e)

    finally:
        conn.close()


# -----------------------------
# MAIN
# -----------------------------
def main():
    create_schema_and_tables()


if __name__ == "__main__":
    main()
