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
# 2. Create analysis columns
# --------------------------------------------------

df["IsCancellation"] = (
    df["Invoice"]
    .astype(str)
    .str.startswith("C")
)

df["LineValue"] = df["Quantity"] * df["Price"]

df["IsPositiveSale"] = (
    (df["Quantity"] > 0) &
    (df["Price"] > 0) &
    (~df["IsCancellation"])
)

df["IsReturn"] = df["Quantity"] < 0

# --------------------------------------------------
# 3. Invoice analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("INVOICE ANALYSIS")
print("=" * 60)

total_invoices = df["Invoice"].nunique()

cancelled_invoices = df.loc[
    df["IsCancellation"],
    "Invoice"
].nunique()

positive_invoices = df.loc[
    df["IsPositiveSale"],
    "Invoice"
].nunique()

print(f"Unique invoices: {total_invoices:,}")
print(f"Cancelled invoices: {cancelled_invoices:,}")
print(f"Positive sales invoices: {positive_invoices:,}")

# --------------------------------------------------
# 4. Quantity analysis
# --------------------------------------------------

print("\n" + "=" * 60)
print("QUANTITY ANALYSIS")
print("=" * 60)

quantity_sold = df.loc[
    df["IsPositiveSale"],
    "Quantity"
].sum()

quantity_returned = abs(
    df.loc[
        df["IsReturn"],
        "Quantity"
    ].sum()
)

print(f"Quantity sold: {quantity_sold:,.0f}")
print(f"Quantity returned: {quantity_returned:,.0f}")

# --------------------------------------------------
# 5. Sales and returns
# --------------------------------------------------

print("\n" + "=" * 60)
print("SALES / RETURN VALUE")
print("=" * 60)

sales_value = df.loc[
    df["IsPositiveSale"],
    "LineValue"
].sum()

return_value = abs(
    df.loc[
        df["IsReturn"],
        "LineValue"
    ].sum()
)

net_value = sales_value - return_value

print(f"Gross sales value: £{sales_value:,.2f}")
print(f"Return value: £{return_value:,.2f}")
print(f"Net transaction value: £{net_value:,.2f}")

# --------------------------------------------------
# 6. Non-cancellation negative quantities
# --------------------------------------------------

print("\n" + "=" * 60)
print("NEGATIVE QUANTITY WITHOUT CANCELLATION")
print("=" * 60)

non_cancelled_returns = df[
    df["IsReturn"] &
    ~df["IsCancellation"]
]

print(
    f"Rows: {len(non_cancelled_returns):,}"
)

print(
    f"Value: £{abs(non_cancelled_returns['LineValue'].sum()):,.2f}"
)

print("\nExamples:")

print(
    non_cancelled_returns[
        [
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "Price",
            "Customer ID",
            "Country"
        ]
    ].head(20)
)

# --------------------------------------------------
# 7. Yearly sales
# --------------------------------------------------

print("\n" + "=" * 60)
print("YEARLY SALES")
print("=" * 60)

sales_df = df[df["IsPositiveSale"]].copy()

sales_df["Year"] = sales_df["InvoiceDate"].dt.year

yearly_sales = (
    sales_df
    .groupby("Year")["LineValue"]
    .agg(["sum", "count"])
)

print(yearly_sales)

# --------------------------------------------------
# 8. Country sales
# --------------------------------------------------

print("\n" + "=" * 60)
print("TOP 10 COUNTRIES BY SALES")
print("=" * 60)

country_sales = (
    sales_df
    .groupby("Country")["LineValue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print(country_sales)

# --------------------------------------------------
# 9. Top products
# --------------------------------------------------

print("\n" + "=" * 60)
print("TOP 10 PRODUCTS BY SALES")
print("=" * 60)

product_sales = (
    sales_df
    .groupby(
        ["StockCode", "Description"]
    )["LineValue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print(product_sales)

# --------------------------------------------------
# 10. Monthly sales
# --------------------------------------------------

print("\n" + "=" * 60)
print("MONTHLY SALES")
print("=" * 60)

sales_df["YearMonth"] = (
    sales_df["InvoiceDate"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    sales_df
    .groupby("YearMonth")["LineValue"]
    .sum()
)

print(monthly_sales.head(15))

# --------------------------------------------------
# 11. Final summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("FINAL QUALITY CHECK COMPLETE")
print("=" * 60)