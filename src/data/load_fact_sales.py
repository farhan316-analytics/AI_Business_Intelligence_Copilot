import pandas as pd
import psycopg2
from pathlib import Path
from getpass import getpass
from io import StringIO

# --------------------------------------------------
# PostgreSQL connection
# --------------------------------------------------

DB_NAME = "ai_bi_copilot"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

password = getpass("Enter PostgreSQL password: ")

# --------------------------------------------------
# Load Parquet
# --------------------------------------------------

file_path = Path(
    "data/processed/database/fact_sales.parquet"
)

print("\nLoading fact_sales parquet...")

df = pd.read_parquet(file_path)

print(f"Rows loaded: {len(df):,}")

# --------------------------------------------------
# Prepare database columns
# --------------------------------------------------

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


# Customer IDs came from Excel as floats because
# missing values were present. Convert valid IDs
# to integers and preserve missing values as NULL.

df["customer_id"] = (
    pd.to_numeric(df["customer_id"], errors="coerce")
    .round()
    .astype("Int64")
)
# Convert dates to strings PostgreSQL understands
df["invoice_date"] = pd.to_datetime(
    df["invoice_date"]
).dt.strftime("%Y-%m-%d %H:%M:%S")

df["order_date"] = pd.to_datetime(
    df["order_date"]
).dt.strftime("%Y-%m-%d")

# --------------------------------------------------
# Convert to CSV in memory
# --------------------------------------------------

print("Preparing data for PostgreSQL COPY...")

buffer = StringIO()

df.to_csv(
    buffer,
    index=False,
    header=False,
    na_rep="\\N"
)

buffer.seek(0)

# --------------------------------------------------
# Connect
# --------------------------------------------------

print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=password,
)

cursor = connection.cursor()

# --------------------------------------------------
# Load using COPY
# --------------------------------------------------

print("Loading 1M+ rows into PostgreSQL...")
print("This may take a little while.")

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

try:

    cursor.copy_expert(
        copy_sql,
        buffer
    )

    connection.commit()

    print("✓ Fact table loaded successfully.")

except Exception as e:

    connection.rollback()

    print("\nERROR:")
    print(e)

    raise

finally:

    cursor.close()
    connection.close()

# --------------------------------------------------
# Final message
# --------------------------------------------------

print("\n" + "=" * 60)
print("FACT SALES LOADING COMPLETE")
print("=" * 60)

print(f"Rows loaded: {len(df):,}")
print(f"Revenue: £{df['revenue'].sum():,.2f}")