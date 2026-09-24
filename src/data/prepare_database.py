import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

input_file = Path("data/processed/clean_sales_data.parquet")
output_dir = Path("data/processed/database")
output_dir.mkdir(parents=True, exist_ok=True)

print("Loading cleaned sales data...")

df = pd.read_parquet(input_file)

print(f"Rows loaded: {len(df):,}")

# --------------------------------------------------
# Create database-ready sales table
# --------------------------------------------------

sales = df[
    [
        "invoice",
        "invoice_date",
        "year",
        "month",
        "year_month",
        "day_of_week",
        "customer_id",
        "customer_status",
        "stockcode",
        "description",
        "country",
        "quantity",
        "price",
        "line_value",
    ]
].copy()

# --------------------------------------------------
# Rename fields for database consistency
# --------------------------------------------------

sales = sales.rename(
    columns={
        "stockcode": "product_key",
        "price": "unit_price",
        "line_value": "revenue",
    }
)

# --------------------------------------------------
# Date fields
# --------------------------------------------------

sales["invoice_date"] = pd.to_datetime(sales["invoice_date"])

sales["order_date"] = sales["invoice_date"].dt.date

sales["year"] = sales["invoice_date"].dt.year

sales["quarter"] = sales["invoice_date"].dt.quarter

sales["month"] = sales["invoice_date"].dt.month

sales["year_month"] = (
    sales["invoice_date"]
    .dt.to_period("M")
    .astype(str)
)

sales["day"] = sales["invoice_date"].dt.day

sales["hour"] = sales["invoice_date"].dt.hour

# --------------------------------------------------
# Customer key
# --------------------------------------------------

sales["customer_key"] = (
    sales["customer_id"]
    .fillna(0)
    .astype(int)
)

# --------------------------------------------------
# Product key
# --------------------------------------------------

sales["product_key"] = (
    sales["product_key"]
    .astype(str)
    .str.strip()
)

# --------------------------------------------------
# Remove accidental duplicates
# --------------------------------------------------

before = len(sales)

sales = sales.drop_duplicates()

duplicates_removed = before - len(sales)

# --------------------------------------------------
# Final fact table columns
# --------------------------------------------------

sales = sales[
    [
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
]

# --------------------------------------------------
# Save fact_sales
# --------------------------------------------------

fact_file = output_dir / "fact_sales.parquet"

sales.to_parquet(
    fact_file,
    index=False
)

# --------------------------------------------------
# Product dimension
# --------------------------------------------------

dim_product = (
    sales[
        [
            "product_key",
            "description",
        ]
    ]
    .drop_duplicates(subset=["product_key"])
    .sort_values("product_key")
)

product_file = output_dir / "dim_product.parquet"

dim_product.to_parquet(
    product_file,
    index=False
)

# --------------------------------------------------
# Customer dimension
# --------------------------------------------------

dim_customer = (
    sales[
        [
            "customer_key",
            "customer_id",
            "customer_status",
        ]
    ]
    .drop_duplicates(subset=["customer_key"])
    .sort_values("customer_key")
)

customer_file = output_dir / "dim_customer.parquet"

dim_customer.to_parquet(
    customer_file,
    index=False
)

# --------------------------------------------------
# Date dimension
# --------------------------------------------------

date_range = pd.date_range(
    start=sales["invoice_date"].min().normalize(),
    end=sales["invoice_date"].max().normalize(),
    freq="D",
)

dim_date = pd.DataFrame(
    {
        "date": date_range,
    }
)

dim_date["year"] = dim_date["date"].dt.year
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["month"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.month_name()
dim_date["year_month"] = (
    dim_date["date"]
    .dt.to_period("M")
    .astype(str)
)
dim_date["day"] = dim_date["date"].dt.day
dim_date["day_of_week"] = dim_date["date"].dt.day_name()
dim_date["week"] = (
    dim_date["date"]
    .dt.isocalendar()
    .week
    .astype(int)
)

date_file = output_dir / "dim_date.parquet"

dim_date.to_parquet(
    date_file,
    index=False
)

# --------------------------------------------------
# Final validation
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATABASE PREPARATION COMPLETE")
print("=" * 60)

print(f"Fact sales rows:       {len(sales):,}")
print(f"Duplicates removed:    {duplicates_removed:,}")
print(f"Revenue:               £{sales['revenue'].sum():,.2f}")

print(f"\nProducts:              {len(dim_product):,}")
print(f"Customers:             {len(dim_customer):,}")
print(f"Dates:                 {len(dim_date):,}")

print("\nFact sales columns:")
print(sales.columns.tolist())

print("\nFiles created:")
print(f"✓ {fact_file}")
print(f"✓ {product_file}")
print(f"✓ {customer_file}")
print(f"✓ {date_file}")

print("\nDatabase structure:")
print(
    """
fact_sales
    │
    ├── product_key ──→ dim_product
    │
    ├── customer_key ─→ dim_customer
    │
    └── order_date ───→ dim_date
"""
)

print("Database preparation successful.")