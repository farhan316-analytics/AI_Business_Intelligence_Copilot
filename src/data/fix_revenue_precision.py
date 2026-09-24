import psycopg2
from getpass import getpass

DB_NAME = "ai_bi_copilot"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

password = getpass("Enter PostgreSQL password: ")

connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=password,
)

cursor = connection.cursor()

print("\nConnected to PostgreSQL.")
print("Removing dependent analytics views...")

# --------------------------------------------------
# Drop views temporarily
# --------------------------------------------------

views = [
    "vw_top_customers",
    "vw_top_products",
    "vw_kpis",
    "vw_customer_sales",
    "vw_product_sales",
    "vw_country_sales",
    "vw_monthly_sales",
]

for view in views:
    cursor.execute(
        f"DROP VIEW IF EXISTS analytics.{view};"
    )

connection.commit()

print("✓ Analytics views removed temporarily.")

# --------------------------------------------------
# Change revenue precision
# --------------------------------------------------

print("Updating revenue precision...")

cursor.execute("""
    ALTER TABLE analytics.fact_sales
    ALTER COLUMN revenue TYPE NUMERIC(14,4);
""")

connection.commit()

print("✓ Revenue column changed to NUMERIC(14,4).")

# --------------------------------------------------
# Check revenue
# --------------------------------------------------

cursor.execute("""
    SELECT SUM(revenue)
    FROM analytics.fact_sales;
""")

revenue = cursor.fetchone()[0]

print(
    f"\nPostgreSQL revenue: £{revenue:,.4f}"
)

cursor.close()
connection.close()

print("\nRevenue precision update complete.")
print("Analytics views will be recreated in the next step.")