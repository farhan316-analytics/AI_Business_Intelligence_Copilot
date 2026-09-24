import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME")
)

cur = conn.cursor()

views = [
    "vw_kpis",
    "vw_monthly_sales",
    "vw_country_sales",
    "vw_product_sales",
    "vw_customer_sales",
    "vw_top_products",
    "vw_top_customers",
]

for view in views:
    print(f"\n{'=' * 60}")
    print(view)
    print("=" * 60)

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'analytics'
          AND table_name = %s
        ORDER BY ordinal_position;
    """, (view,))

    for row in cur.fetchall():
        print(row[0])

cur.close()
conn.close()