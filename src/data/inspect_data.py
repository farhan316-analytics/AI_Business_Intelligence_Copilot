import pandas as pd
from pathlib import Path

# Dataset location
file_path = Path("data/raw/online_retail_II.xlsx")

print("Loading dataset...")

# Load Excel file
sheets = pd.read_excel(
    file_path,
    sheet_name=None,
    engine="calamine"
)

print(f"Sheets found: {list(sheets.keys())}")

df = pd.concat(sheets.values(), ignore_index=True)

print(f"Total sheets loaded: {len(sheets)}")

print("\nDataset loaded successfully!")

print("\n" + "=" * 60)
print("DATASET SHAPE")
print("=" * 60)

print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")

print("\n" + "=" * 60)
print("COLUMNS")
print("=" * 60)

print(df.columns.tolist())

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

print(df.isnull().sum())

print("\n" + "=" * 60)
print("DUPLICATES")
print("=" * 60)

print(f"Duplicate rows: {df.duplicated().sum():,}")

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)

print(df.head())

print("\n" + "=" * 60)
print("DATE RANGE")
print("=" * 60)

print(f"Minimum date: {df['InvoiceDate'].min()}")
print(f"Maximum date: {df['InvoiceDate'].max()}")

print("\n" + "=" * 60)
print("CANCELLATIONS")
print("=" * 60)

cancellations = df["Invoice"].astype(str).str.startswith("C").sum()

print(f"Cancellation rows: {cancellations:,}")

print("\n" + "=" * 60)
print("NEGATIVE QUANTITIES")
print("=" * 60)

print(f"Negative quantity rows: {(df['Quantity'] < 0).sum():,}")

print("\n" + "=" * 60)
print("INVALID PRICES")
print("=" * 60)

print(f"Zero/negative price rows: {(df['Price'] <= 0).sum():,}")

print("\n" + "=" * 60)
print("UNIQUE VALUES")
print("=" * 60)

print(f"Unique customers: {df['Customer ID'].nunique():,}")
print(f"Unique products: {df['StockCode'].nunique():,}")
print(f"Unique countries: {df['Country'].nunique():,}")

print("\n" + "=" * 60)
print("TOP 10 COUNTRIES")
print("=" * 60)

print(df["Country"].value_counts().head(10))

print("\nInspection complete!")