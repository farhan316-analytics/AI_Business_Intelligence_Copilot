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

print("\nConnected successfully.\n")

queries = {
    "Fact sales rows": """
        SELECT COUNT(*)
        FROM analytics.fact_sales;
    """,

    "Total revenue": """
        SELECT ROUND(SUM(revenue), 2)
        FROM analytics.fact_sales;
    """,

    "Total quantity": """
        SELECT SUM(quantity)
        FROM analytics.fact_sales;
    """,

    "Unique invoices": """
        SELECT COUNT(DISTINCT invoice)
        FROM analytics.fact_sales;
    """,

    "Unique products": """
        SELECT COUNT(DISTINCT product_key)
        FROM analytics.fact_sales;
    """,

    "Unique customers": """
        SELECT COUNT(DISTINCT customer_key)
        FROM analytics.fact_sales;
    """,

    "Countries": """
        SELECT COUNT(DISTINCT country)
        FROM analytics.fact_sales;
    """,

    "First date": """
        SELECT MIN(order_date)
        FROM analytics.fact_sales;
    """,

    "Last date": """
        SELECT MAX(order_date)
        FROM analytics.fact_sales;
    """,

    "Invalid quantities": """
        SELECT COUNT(*)
        FROM analytics.fact_sales
        WHERE quantity <= 0;
    """,

    "Invalid prices": """
        SELECT COUNT(*)
        FROM analytics.fact_sales
        WHERE unit_price <= 0;
    """,

    "Orphan customers": """
        SELECT COUNT(*)
        FROM analytics.fact_sales f
        LEFT JOIN analytics.dim_customer c
            ON f.customer_key = c.customer_key
        WHERE c.customer_key IS NULL;
    """,

    "Orphan products": """
        SELECT COUNT(*)
        FROM analytics.fact_sales f
        LEFT JOIN analytics.dim_product p
            ON f.product_key = p.product_key
        WHERE p.product_key IS NULL;
    """,

    "Orphan dates": """
        SELECT COUNT(*)
        FROM analytics.fact_sales f
        LEFT JOIN analytics.dim_date d
            ON f.order_date = d.date
        WHERE d.date IS NULL;
    """
}

print("=" * 60)
print("POSTGRESQL VALIDATION")
print("=" * 60)

for name, query in queries.items():
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(f"{name:<25} {result}")

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)