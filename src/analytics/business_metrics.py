import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_bi_copilot")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def query_to_dataframe(query, params=None):
    """Execute a PostgreSQL query and return a pandas DataFrame."""

    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params
        )


def get_business_kpis():
    """Return overall business KPIs."""

    query = """
        SELECT
            total_revenue,
            total_quantity,
            total_orders,
            total_customers,
            total_products,
            total_countries,
            average_order_value
        FROM analytics.vw_kpis;
    """

    return query_to_dataframe(query)


def get_monthly_sales():
    """Return monthly sales performance."""

    query = """
        SELECT
            year_month,
            month_start,
            revenue,
            quantity,
            orders,
            customers,
            average_order_value,
            previous_month_revenue,
            revenue_growth_pct
        FROM analytics.vw_monthly_sales
        ORDER BY month_start;
    """

    return query_to_dataframe(query)


def get_country_performance(limit=20):
    """Return country-level sales performance."""

    query = """
        SELECT
            country,
            revenue,
            quantity,
            orders,
            customers,
            average_order_value
        FROM analytics.vw_country_sales
        ORDER BY revenue DESC
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


def get_product_performance(limit=20):
    """Return product-level sales performance."""

    query = """
        SELECT
            product_key,
            description,
            quantity_sold,
            revenue,
            orders,
            customers,
            average_order_value
        FROM analytics.vw_product_sales
        ORDER BY revenue DESC
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


def get_customer_performance(limit=20):
    """Return customer-level sales performance."""

    query = """
        SELECT
            customer_key,
            customer_id,
            orders,
            quantity,
            revenue,
            first_order_date,
            last_order_date,
            average_order_value
        FROM analytics.vw_customer_sales
        WHERE customer_key <> 0
        ORDER BY revenue DESC
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


def get_top_products(limit=10):
    """Return top products ranked by revenue."""

    query = """
        SELECT
            product_key,
            description,
            quantity_sold,
            revenue,
            orders,
            customers,
            average_order_value,
            revenue_rank
        FROM analytics.vw_top_products
        ORDER BY revenue_rank
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


def get_top_customers(limit=10):
    """Return top customers ranked by revenue."""

    query = """
        SELECT
            customer_key,
            customer_id,
            orders,
            quantity,
            revenue,
            first_order_date,
            last_order_date,
            average_order_value,
            revenue_rank
        FROM analytics.vw_top_customers
        WHERE customer_key <> 0
        ORDER BY revenue_rank
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


def get_revenue_declines(limit=5):
    """Return months with the largest revenue declines."""

    query = """
        SELECT
            year_month,
            month_start,
            revenue,
            previous_month_revenue,
            revenue_growth_pct
        FROM analytics.vw_monthly_sales
        WHERE revenue_growth_pct IS NOT NULL
          AND revenue_growth_pct < 0
        ORDER BY revenue_growth_pct ASC
        LIMIT :limit;
    """

    return query_to_dataframe(query, {"limit": limit})


if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS INTELLIGENCE COPILOT")
    print("BUSINESS METRICS TEST")
    print("=" * 70)

    print("\nOVERALL KPIs")
    print(get_business_kpis().to_string(index=False))

    print("\nMONTHLY SALES")
    print(get_monthly_sales().tail(5).to_string(index=False))

    print("\nTOP COUNTRIES")
    print(get_country_performance(5).to_string(index=False))

    print("\nTOP PRODUCTS")
    print(get_product_performance(5).to_string(index=False))

    print("\nTOP CUSTOMERS")
    print(get_customer_performance(5).to_string(index=False))

    print("\nREVENUE DECLINES")
    print(get_revenue_declines(5).to_string(index=False))

    print("\n" + "=" * 70)
    print("ANALYTICS LAYER TEST COMPLETE")
    print("=" * 70)