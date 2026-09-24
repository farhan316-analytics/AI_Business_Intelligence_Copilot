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


def run_query(title, query):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)


# --------------------------------------------------
# 1. Overall KPIs
# --------------------------------------------------

run_query(
    "OVERALL BUSINESS KPIs",
    """
    SELECT *
    FROM analytics.vw_kpis;
    """
)


# --------------------------------------------------
# 2. Monthly sales
# --------------------------------------------------

run_query(
    "MONTHLY SALES",
    """
    SELECT
        year_month,
        ROUND(revenue, 2) AS revenue,
        orders,
        customers,
        average_order_value,
        revenue_growth_pct
    FROM analytics.vw_monthly_sales
    ORDER BY month_start;
    """
)


# --------------------------------------------------
# 3. Top countries
# --------------------------------------------------

run_query(
    "TOP 10 COUNTRIES BY REVENUE",
    """
    SELECT
        country,
        ROUND(revenue, 2) AS revenue,
        orders,
        customers,
        average_order_value
    FROM analytics.vw_country_sales
    ORDER BY revenue DESC
    LIMIT 10;
    """
)


# --------------------------------------------------
# 4. Top products
# --------------------------------------------------

run_query(
    "TOP 10 PRODUCTS BY REVENUE",
    """
    SELECT
        product_key,
        description,
        quantity_sold,
        ROUND(revenue, 2) AS revenue,
        orders
    FROM analytics.vw_top_products
    ORDER BY revenue_rank
    LIMIT 10;
    """
)


# --------------------------------------------------
# 5. Top customers
# --------------------------------------------------

run_query(
    "TOP 10 CUSTOMERS BY REVENUE",
    """
    SELECT
        customer_id,
        orders,
        quantity,
        ROUND(revenue, 2) AS revenue,
        average_order_value,
        first_order_date,
        last_order_date
    FROM analytics.vw_top_customers
    ORDER BY revenue_rank
    LIMIT 10;
    """
)


# --------------------------------------------------
# 6. Biggest monthly decline
# --------------------------------------------------

run_query(
    "MONTHS WITH LARGEST REVENUE DECLINES",
    """
    SELECT
        year_month,
        ROUND(revenue, 2) AS revenue,
        ROUND(previous_month_revenue, 2) AS previous_month_revenue,
        revenue_growth_pct
    FROM analytics.vw_monthly_sales
    WHERE revenue_growth_pct IS NOT NULL
    ORDER BY revenue_growth_pct ASC
    LIMIT 5;
    """
)


cursor.close()
connection.close()

print("\n" + "=" * 70)
print("ANALYTICS TEST COMPLETE")
print("=" * 70)