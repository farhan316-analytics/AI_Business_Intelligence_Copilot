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
print("Creating analytics views...\n")


sql = """

CREATE SCHEMA IF NOT EXISTS analytics;


CREATE OR REPLACE VIEW analytics.vw_monthly_sales AS

WITH monthly AS (

    SELECT
        year_month,
        MIN(order_date) AS month_start,
        SUM(revenue) AS revenue,
        SUM(quantity) AS quantity,
        COUNT(DISTINCT invoice) AS orders,
        COUNT(
            DISTINCT CASE
                WHEN customer_key <> 0
                THEN customer_key
            END
        ) AS customers

    FROM analytics.fact_sales

    GROUP BY year_month
)

SELECT
    year_month,
    month_start,
    revenue,
    quantity,
    orders,
    customers,

    ROUND(
        revenue / NULLIF(orders, 0),
        2
    ) AS average_order_value,

    LAG(revenue) OVER (
        ORDER BY month_start
    ) AS previous_month_revenue,

    ROUND(
        (
            revenue
            - LAG(revenue) OVER (
                ORDER BY month_start
            )
        )
        /
        NULLIF(
            LAG(revenue) OVER (
                ORDER BY month_start
            ),
            0
        )
        * 100,
        2
    ) AS revenue_growth_pct

FROM monthly;


CREATE OR REPLACE VIEW analytics.vw_country_sales AS

SELECT
    country,
    SUM(revenue) AS revenue,
    SUM(quantity) AS quantity,
    COUNT(DISTINCT invoice) AS orders,

    COUNT(
        DISTINCT CASE
            WHEN customer_key <> 0
            THEN customer_key
        END
    ) AS customers,

    ROUND(
        SUM(revenue)
        / NULLIF(COUNT(DISTINCT invoice), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales

GROUP BY country;


CREATE OR REPLACE VIEW analytics.vw_product_sales AS

SELECT
    product_key,
    MAX(description) AS description,
    SUM(quantity) AS quantity_sold,
    SUM(revenue) AS revenue,
    COUNT(DISTINCT invoice) AS orders,

    COUNT(
        DISTINCT CASE
            WHEN customer_key <> 0
            THEN customer_key
        END
    ) AS customers,

    ROUND(
        SUM(revenue)
        / NULLIF(COUNT(DISTINCT invoice), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales

GROUP BY product_key;


CREATE OR REPLACE VIEW analytics.vw_customer_sales AS

SELECT
    customer_key,
    MAX(customer_id) AS customer_id,
    COUNT(DISTINCT invoice) AS orders,
    SUM(quantity) AS quantity,
    SUM(revenue) AS revenue,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date,

    ROUND(
        SUM(revenue)
        / NULLIF(COUNT(DISTINCT invoice), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales

WHERE customer_key <> 0

GROUP BY customer_key;


CREATE OR REPLACE VIEW analytics.vw_kpis AS

SELECT
    SUM(revenue) AS total_revenue,
    SUM(quantity) AS total_quantity,
    COUNT(DISTINCT invoice) AS total_orders,

    COUNT(
        DISTINCT CASE
            WHEN customer_key <> 0
            THEN customer_key
        END
    ) AS total_customers,

    COUNT(DISTINCT product_key) AS total_products,
    COUNT(DISTINCT country) AS total_countries,

    ROUND(
        SUM(revenue)
        / NULLIF(COUNT(DISTINCT invoice), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales;


CREATE OR REPLACE VIEW analytics.vw_top_products AS

SELECT
    product_key,
    description,
    quantity_sold,
    revenue,
    orders,
    customers,
    average_order_value,

    RANK() OVER (
        ORDER BY revenue DESC
    ) AS revenue_rank

FROM analytics.vw_product_sales;


CREATE OR REPLACE VIEW analytics.vw_top_customers AS

SELECT
    customer_key,
    customer_id,
    orders,
    quantity,
    revenue,
    first_order_date,
    last_order_date,
    average_order_value,

    RANK() OVER (
        ORDER BY revenue DESC
    ) AS revenue_rank

FROM analytics.vw_customer_sales;

"""

try:

    cursor.execute(sql)
    connection.commit()

    print("✓ Analytics views created successfully.")

    # Verify views
    cursor.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'analytics'
        ORDER BY table_name;
    """)

    views = cursor.fetchall()

    print("\nAnalytics views:")

    for view in views:
        print(f"✓ {view[0]}")

except Exception as e:

    connection.rollback()

    print("\nERROR:")
    print(e)

    raise

finally:

    cursor.close()
    connection.close()


print("\nAnalytics layer complete.")