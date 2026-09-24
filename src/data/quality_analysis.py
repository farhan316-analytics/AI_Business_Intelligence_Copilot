import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Load complete dataset
# --------------------------------------------------

file_path = Path("data/raw/online_retail_II.xlsx")

print("Loading dataset...")

sheets = pd.read_excel(
    file_path,
    sheet_name=None,
    engine="calamine"
)

df = pd.concat(sheets.values(), ignore_index=True)

print(f"Rows loaded: {len(df):,}")

# --------------------------------------------------
# 2. Create flags
# --------------------------------------------------

df["IsCancellation"] = (
    df["Invoice"]
    .astype(str)
    .str.startswith("C")
)

df["IsNegativeQuantity"] = df["Quantity"] < 0

df["IsInvalidPrice"] = df["Price"] <= 0

df["IsDuplicate"] = df.duplicated(keep=False)

df["MissingCustomer"] = df["Customer ID"].isna()

# --------------------------------------------------
# 3. Cancellation vs negative quantity
# --------------------------------------------------

print("\n" + "=" * 60)
print("CANCELLATION / NEGATIVE QUANTITY ANALYSIS")
print("=" * 60)

print(
    "Cancellation rows:",
    df["IsCancellation"].sum()
)

print(
    "Negative quantity rows:",
    df["IsNegativeQuantity"].sum()
)

print(
    "Cancellation rows with negative quantity:",
    (
        df["IsCancellation"] &
        df["IsNegativeQuantity"]
    ).sum()
)

print(
    "Negative quantity rows that are NOT cancellations:",
    (
        df["IsNegativeQuantity"] &
        ~df["IsCancellation"]
    ).sum()
)

# --------------------------------------------------
# 4. Invalid prices
# --------------------------------------------------

print("\n" + "=" * 60)
print("INVALID PRICE ANALYSIS")
print("=" * 60)

print(
    "Zero/negative price rows:",
    df["IsInvalidPrice"].sum()
)

print("\nExamples:")

print(
    df.loc[
        df["IsInvalidPrice"],
        ["Invoice", "StockCode", "Description",
         "Quantity", "Price", "Country"]
    ].head(20)
)

# --------------------------------------------------
# 5. Duplicates
# --------------------------------------------------

print("\n" + "=" * 60)
print("DUPLICATE ANALYSIS")
print("=" * 60)

print(
    "Duplicate rows:",
    df.duplicated().sum()
)

print(
    "Rows belonging to duplicate groups:",
    df["IsDuplicate"].sum()
)

print("\nExample duplicate rows:")

print(
    df.loc[
        df["IsDuplicate"],
        [
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID"
        ]
    ].head(20)
)

# --------------------------------------------------
# 6. Missing customers
# --------------------------------------------------

print("\n" + "=" * 60)
print("MISSING CUSTOMER ANALYSIS")
print("=" * 60)

print(
    "Missing Customer IDs:",
    df["MissingCustomer"].sum()
)

print(
    "Missing Customer ID + positive quantity:",
    (
        df["MissingCustomer"] &
        (df["Quantity"] > 0)
    ).sum()
)

print(
    "Missing Customer ID + negative quantity:",
    (
        df["MissingCustomer"] &
        (df["Quantity"] < 0)
    ).sum()
)

# --------------------------------------------------
# 7. Revenue analysis
# --------------------------------------------------

df["LineRevenue"] = df["Quantity"] * df["Price"]

print("\n" + "=" * 60)
print("REVENUE ANALYSIS")
print("=" * 60)

print(
    f"Gross transaction value: "
    f"{df['LineRevenue'].sum():,.2f}"
)

print(
    f"Positive-quantity revenue: "
    f"{df.loc[df['Quantity'] > 0, 'LineRevenue'].sum():,.2f}"
)

print(
    f"Negative-quantity value: "
    f"{df.loc[df['Quantity'] < 0, 'LineRevenue'].sum():,.2f}"
)

# --------------------------------------------------
# 8. Free / zero-price products
# --------------------------------------------------

print("\n" + "=" * 60)
print("ZERO-PRICE PRODUCT ANALYSIS")
print("=" * 60)

zero_price = df[df["Price"] == 0]

print(
    f"Zero-price rows: {len(zero_price):,}"
)

print(
    f"Unique zero-price products: "
    f"{zero_price['StockCode'].nunique():,}"
)

print("\nMost common zero-price products:")

print(
    zero_price["Description"]
    .value_counts()
    .head(15)
)

# --------------------------------------------------
# 9. Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("QUALITY ANALYSIS COMPLETE")
print("=" * 60)