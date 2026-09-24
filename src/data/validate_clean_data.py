import pandas as pd
from pathlib import Path

file_path = Path("data/processed/clean_sales_data.parquet")

print("Loading cleaned sales data...")
df = pd.read_parquet(file_path)

print("\n" + "=" * 60)
print("CLEANED DATA VALIDATION")
print("=" * 60)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())

print("\nBasic checks:")
print(f"Negative quantities: {(df['quantity'] < 0).sum():,}")
print(f"Zero/negative prices: {(df['price'] <= 0).sum():,}")
print(f"Cancellations: {df['is_cancellation'].sum():,}")
print(f"Service items: {df['is_service_item'].sum():,}")
print(f"Valid sales flags: {df['is_valid_sale'].sum():,}")

print("\nSales validation:")
print(f"Sales value: £{df['line_value'].sum():,.2f}")
print(f"Unique invoices: {df['invoice'].nunique():,}")
print(f"Unique customers: {df['customer_id'].nunique():,}")
print(f"Unique products: {df['stockcode'].nunique():,}")
print(f"Countries: {df['country'].nunique():,}")

print("\nDate range:")
print(f"Start: {df['invoice_date'].min()}")
print(f"End:   {df['invoice_date'].max()}")

print("\nMissing values:")
print(df.isna().sum())

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)