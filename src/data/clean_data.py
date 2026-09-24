import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

input_file = Path("data/raw/online_retail_II.xlsx")
output_dir = Path("data/processed")

output_dir.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Load both Excel sheets
# --------------------------------------------------

print("Loading raw dataset...")

sheets = pd.read_excel(
    input_file,
    sheet_name=None,
    engine="calamine"
)

df = pd.concat(
    sheets.values(),
    ignore_index=True
)

print(f"Raw rows: {len(df):,}")

# --------------------------------------------------
# 3. Standardize column names
# --------------------------------------------------

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

print("Columns after cleaning:")
print(df.columns.tolist())

# --------------------------------------------------
# 4. Basic data types
# --------------------------------------------------

df["invoice"] = df["invoice"].astype(str).str.strip()

df["stockcode"] = (
    df["stockcode"]
    .astype(str)
    .str.strip()
)

df["description"] = (
    df["description"]
    .astype("string")
    .str.strip()
)

df["country"] = (
    df["country"]
    .astype(str)
    .str.strip()
)

df["invoicedate"] = pd.to_datetime(df["invoicedate"])
df = df.rename(columns={"invoicedate": "invoice_date"})

# --------------------------------------------------
# 5. Remove exact duplicate rows
# --------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates()

duplicates_removed = (
    before_duplicates - len(df)
)

print(
    f"Exact duplicates removed: "
    f"{duplicates_removed:,}"
)

# --------------------------------------------------
# 6. Create transaction flags
# --------------------------------------------------

df["is_cancellation"] = (
    df["invoice"]
    .str.startswith("C")
)

df["is_return"] = (
    df["quantity"] < 0
)

df["is_valid_price"] = (
    df["price"] > 0
)

# --------------------------------------------------
# 7. Calculate transaction value
# --------------------------------------------------

df["line_value"] = (
    df["quantity"] *
    df["price"]
)

# --------------------------------------------------
# 8. Identify operational/service codes
# --------------------------------------------------

service_codes = {
    "M",
    "DOT",
    "POST",
    "BANK CHARGES",
    "AMAZONFEE",
    "CRUK",
    "C2",
    "D",
    "S",
    "gift_0001",
    "gift_0002",
    "gift_0003",
    "gift_0004",
    "gift_0005"
}

df["is_service_item"] = (
    df["stockcode"]
    .str.upper()
    .isin(service_codes)
)

# --------------------------------------------------
# 9. Identify valid sales
# --------------------------------------------------

df["is_valid_sale"] = (
    (df["quantity"] > 0)
    & (df["price"] > 0)
    & (~df["is_cancellation"])
    & (~df["is_service_item"])
)

# --------------------------------------------------
# 10. Create sales dataset
# --------------------------------------------------

sales_df = df[
    df["is_valid_sale"]
].copy()

# --------------------------------------------------
# 11. Create returns dataset
# --------------------------------------------------

returns_df = df[
    (df["quantity"] < 0)
    & (df["price"] > 0)
].copy()

# --------------------------------------------------
# 12. Create date attributes
# --------------------------------------------------

sales_df["year"] = (
    sales_df["invoice_date"].dt.year
)

sales_df["month"] = (
    sales_df["invoice_date"].dt.month
)

sales_df["year_month"] = (
    sales_df["invoice_date"]
    .dt.to_period("M")
    .astype(str)
)

sales_df["day_of_week"] = (
    sales_df["invoice_date"]
    .dt.day_name()
)

# --------------------------------------------------
# 13. Customer status
# --------------------------------------------------

sales_df["customer_status"] = (
    sales_df["customer_id"]
    .notna()
    .map({
        True: "Identified",
        False: "Unknown"
    })
)

# --------------------------------------------------
# 14. Save processed data
# --------------------------------------------------

output_file = (
    output_dir /
    "clean_sales_data.parquet"
)

sales_df.to_parquet(
    output_file,
    index=False
)

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(
    f"Raw rows: {len(df):,}"
)

print(
    f"Valid sales rows: {len(sales_df):,}"
)

print(
    f"Rows removed from sales dataset: "
    f"{len(df) - len(sales_df):,}"
)

print(
    f"Sales value: "
    f"£{sales_df['line_value'].sum():,.2f}"
)

print(
    f"Unique customers: "
    f"{sales_df['customer_id'].nunique():,}"
)

print(
    f"Unique products: "
    f"{sales_df['stockcode'].nunique():,}"
)

print(
    f"Countries: "
    f"{sales_df['country'].nunique():,}"
)

print(
    f"\nSaved to:\n{output_file}"
)