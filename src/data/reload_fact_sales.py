import pandas as pd
import psycopg2
from pathlib import Path
from getpass import getpass
from io import StringIO

DB_NAME = "ai_bi_copilot"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

password = getpass("Enter PostgreSQL password: ")

file_path = Path(
    "data/processed/database/fact_sales.parquet"
)

print("\nLoading original fact_sales Parquet...")
df = pd.read_parquet(file_path)

print(f"Rows loaded: {len(df):,}")

columns = [
    "invoice",
    "invoice_date",
    "order_date",
    "year",
    "quarter",
    "month",
    "year_month",
    "day",
    "hour",
    "day_of_week",
    "customer_key",
    "customer_id",
    "customer_status",
    "product_key",
    "description",
    "country",
    "quantity",
    "unit_price",
    "revenue",
]

df = df[columns].copy()

# Convert Customer ID to PostgreSQL-compatible integer/NULL
df["customer_id"] = (
    pd.to_numeric(df["customer_id"], errors="coerce")
    .round()
    .astype("Int64")
)

# Dates
df["invoice_date"] = pd.to_datetime(
    df["invoice_date"]
).dt.strftime("%Y-%m-%d %H:%M:%S")

df["order_date"] = pd.to_datetime(
    df["order_date"]
).dt.strftime("%Y-%m-%d")

print(
    f"Source revenue: £{df['revenue'].sum():,.4f}"
)

print("\nPreparing COPY data...")

buffer = StringIO()

df.to_csv(
    buffer,
    index=False,
    header=False,
    na_rep="\\N",
)

buffer.seek(0)

print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=password,
)

cursor = connection.cursor()

try:

    # Remove the previously loaded fact rows.
    # Dimensions remain untouched.
    print("\nClearing existing fact_sales...")

    cursor.execute("""
        TRUNCATE TABLE analytics.fact_sales;
    """)

    print("✓ Existing fact_sales cleared.")

    print("\nLoading corrected fact_sales...")

    copy_sql = """
    COPY analytics.fact_sales (
        invoice,
        invoice_date,
        order_date,
        year,
        quarter,
        month,
        year_month,
        day,
        hour,
        day_of_week,
        customer_key,
        customer_id,
        customer_status,
        product_key,
        description,
        country,
        quantity,
        unit_price,
        revenue
    )
    FROM STDIN
    WITH (
        FORMAT CSV,
        NULL '\\N'
    )
    """

    cursor.copy_expert(
        copy_sql,
        buffer
    )

    connection.commit()

    print("✓ Fact table reloaded successfully.")

    # Verify
    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(revenue)
        FROM analytics.fact_sales;
    """)

    row_count, revenue = cursor.fetchone()

    print("\n" + "=" * 60)
    print("FACT TABLE RELOAD COMPLETE")
    print("=" * 60)

    print(f"Rows in PostgreSQL: {row_count:,}")
    print(f"Revenue in PostgreSQL: £{revenue:,.4f}")

except Exception as e:

    connection.rollback()

    print("\nERROR:")
    print(e)

    raise

finally:

    cursor.close()
    connection.close()