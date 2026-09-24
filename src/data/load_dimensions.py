import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from getpass import getpass

# --------------------------------------------------
# PostgreSQL connection
# --------------------------------------------------

DB_NAME = "ai_bi_copilot"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

password = getpass("Enter PostgreSQL password: ")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --------------------------------------------------
# Test connection
# --------------------------------------------------

print("\nConnecting to PostgreSQL...")

with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database();"))
    print(f"Connected to: {result.scalar()}")

# --------------------------------------------------
# Files
# --------------------------------------------------

data_dir = Path("data/processed/database")

files = {
    "dim_date": data_dir / "dim_date.parquet",
    "dim_product": data_dir / "dim_product.parquet",
    "dim_customer": data_dir / "dim_customer.parquet",
}

# --------------------------------------------------
# Load dimensions
# --------------------------------------------------

for table_name, file_path in files.items():

    print(f"\nLoading {table_name}...")

    df = pd.read_parquet(file_path)

    print(f"Rows found: {len(df):,}")

    df.to_sql(
        name=table_name,
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print(f"✓ {table_name} loaded")

# --------------------------------------------------
# Validate PostgreSQL counts
# --------------------------------------------------

print("\n" + "=" * 60)
print("POSTGRESQL VALIDATION")
print("=" * 60)

with engine.connect() as connection:

    for table_name in files:

        result = connection.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM analytics.{table_name};
                """
            )
        )

        count = result.scalar()

        print(f"{table_name:<20} {count:,} rows")

print("\nDimension loading complete.")