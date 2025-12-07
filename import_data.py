import pandas as pd
import pymysql
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

# ============================================================================
# STEP 1: Load raw data from Excel
# ============================================================================

print("=" * 80)
print("E-COMMERCE DATA IMPORT & CLEANING PIPELINE")
print("=" * 80)

print("\n[STEP 1] Loading raw data from Excel...\n")

# Load the Excel file
file_path = 'online_retail_II.xlsx'
df = pd.read_excel(file_path)

print(f"✓ Raw data loaded successfully")
print(f"  • Total rows: {len(df):,}")
print(f"  • Total columns: {len(df.columns)}")
print(f"  • Columns: {', '.join(df.columns.tolist())}")
print(f"\nFirst few rows:")
print(df.head(10))

# ============================================================================
# STEP 2: Data cleaning
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 2] Data Cleaning...\n")

# Record original counts for comparison
original_count = len(df)

# Remove rows with missing Customer ID or Description
print("[2.1] Removing rows with missing Customer ID or Description...")
df_clean = df.dropna(subset=['Customer ID', 'Description'])
removed_missing = original_count - len(df_clean)
print(f"  ✓ Removed {removed_missing:,} rows with missing values")
print(f"    Remaining: {len(df_clean):,} rows")

# Remove duplicate rows
print("\n[2.2] Removing duplicate records...")
before_dedup = len(df_clean)
df_clean = df_clean.drop_duplicates()
removed_duplicates = before_dedup - len(df_clean)
print(f"  ✓ Removed {removed_duplicates:,} duplicate rows")
print(f"    Remaining: {len(df_clean):,} rows")

# Remove rows with invalid Quantity (≤ 0)
print("\n[2.3] Removing rows with invalid Quantity (≤ 0)...")
before_qty_filter = len(df_clean)
df_clean = df_clean[df_clean['Quantity'] > 0]
removed_invalid_qty = before_qty_filter - len(df_clean)
print(f"  ✓ Removed {removed_invalid_qty:,} rows with invalid quantity")
print(f"    Remaining: {len(df_clean):,} rows")

# Remove rows with invalid Price (≤ 0)
print("\n[2.4] Removing rows with invalid Price (≤ 0)...")
before_price_filter = len(df_clean)
df_clean = df_clean[df_clean['Price'] > 0]
removed_invalid_price = before_price_filter - len(df_clean)
print(f"  ✓ Removed {removed_invalid_price:,} rows with invalid price")
print(f"    Remaining: {len(df_clean):,} rows")

# Calculate total removed records
total_removed = original_count - len(df_clean)
quality_improvement = (total_removed / original_count) * 100

print(f"\n{'─' * 80}")
print(f"Data Quality Summary:")
print(f"  • Original rows: {original_count:,}")
print(f"  • Final rows: {len(df_clean):,}")
print(f"  • Total removed: {total_removed:,}")
print(f"  • Data quality improvement: {quality_improvement:.1f}%")
print(f"{'─' * 80}")

# ============================================================================
# STEP 3: Prepare data for database import
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 3] Preparing data for database import...\n")

# Convert InvoiceDate to datetime
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

# Create line_total column
df_clean['line_total'] = df_clean['Quantity'] * df_clean['Price']

# Round monetary values
df_clean['Price'] = df_clean['Price'].round(2)
df_clean['line_total'] = df_clean['line_total'].round(2)

print("✓ Data prepared for database import")
print(f"  • Added line_total column")
print(f"  • Standardized data types")
print(f"  • Rounded monetary values to 2 decimals")

# ============================================================================
# STEP 4: Connect to MySQL and create schema
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 4] Connecting to MySQL and creating schema...\n")

conn = pymysql.connect(
    host='localhost',
    user='ecommerce_user',
    password='ecommerce_password',
    database='ecommerce_db'
)
cursor = conn.cursor()

print("✓ MySQL connection established")

# Create tables
print("\n[4.1] Creating database tables...")

# Create customers table
print("  • Creating customers table...")
create_customers_table = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_customers_table)
conn.commit()

# Create products table
print("  • Creating products table...")
create_products_table = """
CREATE TABLE IF NOT EXISTS products (
    stock_code VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_products_table)
conn.commit()

# Create invoices table
print("  • Creating invoices table...")
create_invoices_table = """
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    customer_id INT,
    invoice_date DATETIME,
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
"""
cursor.execute(create_invoices_table)
conn.commit()

# Create order_items table
print("  • Creating order_items table...")
create_order_items_table = """
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id VARCHAR(20),
    stock_code VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10, 2),
    line_total DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
    FOREIGN KEY (stock_code) REFERENCES products(stock_code)
);
"""
cursor.execute(create_order_items_table)
conn.commit()

print("✓ All tables created successfully")

# ============================================================================
# STEP 5: Import data
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 5] Importing data...\n")

# Import unique customers
print("[5.1] Importing customers...")
customers = df_clean[['Customer ID', 'Country']].drop_duplicates()
for _, row in customers.iterrows():
    insert_customer_sql = """
    INSERT IGNORE INTO customers (customer_id, country)
    VALUES (%s, %s)
    """
    cursor.execute(insert_customer_sql, (int(row['Customer ID']), row['Country']))

conn.commit()
print(f"  ✓ Imported {len(customers):,} unique customers")

# Import unique products
print("\n[5.2] Importing products...")
products = df_clean[['StockCode', 'Description']].drop_duplicates()
for _, row in products.iterrows():
    insert_product_sql = """
    INSERT IGNORE INTO products (stock_code, description)
    VALUES (%s, %s)
    """
    cursor.execute(insert_product_sql, (row['StockCode'], row['Description']))

conn.commit()
print(f"  ✓ Imported {len(products):,} unique products")

# Import invoices
print("\n[5.3] Importing invoices...")
invoices = df_clean[['Invoice', 'Customer ID', 'InvoiceDate']].drop_duplicates()

# Group by invoice to calculate total amount
invoice_totals = df_clean.groupby('Invoice')['line_total'].sum().reset_index()
invoice_totals.rename(columns={'line_total': 'total_amount'}, inplace=True)

# Merge with invoice data
invoices_merged = pd.merge(
    invoices,
    invoice_totals,
    left_on='Invoice',
    right_on='Invoice',
    how='left'
)

for _, row in invoices_merged.iterrows():
    insert_invoice_sql = """
    INSERT IGNORE INTO invoices (invoice_id, customer_id, invoice_date, total_amount)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_invoice_sql, (
        row['Invoice'],
        int(row['Customer ID']),
        row['InvoiceDate'],
        row['total_amount']
    ))

conn.commit()
print(f"  ✓ Imported {len(invoices_merged):,} unique invoices")

# Import order items
print("\n[5.4] Importing order items...")
for _, row in df_clean.iterrows():
    insert_order_item_sql = """
    INSERT INTO order_items (invoice_id, stock_code, quantity, unit_price, line_total)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_order_item_sql, (
        row['Invoice'],
        row['StockCode'],
        int(row['Quantity']),
        row['Price'],
        row['line_total']
    ))

conn.commit()
print(f"  ✓ Imported {len(df_clean):,} order items")

# ============================================================================
# STEP 6: Create indexes for performance optimization
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 6] Creating indexes for query optimization...\n")

indexes = [
    ("idx_customer_id", "customers", "customer_id"),
    ("idx_customers_country", "customers", "country"),
    ("idx_invoice_customer", "invoices", "customer_id"),
    ("idx_invoice_date", "invoices", "invoice_date"),
    ("idx_order_items_invoice", "order_items", "invoice_id"),
    ("idx_order_items_stock", "order_items", "stock_code"),
    ("idx_products_stock", "products", "stock_code"),
]

for index_name, table_name, column_name in indexes:
    create_index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
    cursor.execute(create_index_sql)
    print(f"  ✓ Created index: {index_name}")

conn.commit()

# ============================================================================
# STEP 7: Verify import and display summary
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 7] Import verification & summary...\n")

# Count records in each table
cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM products")
product_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM invoices")
invoice_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM order_items")
order_item_count = cursor.fetchone()[0]

print("Import Summary:")
print(f"  • Customers: {customer_count:,}")
print(f"  • Products: {product_count:,}")
print(f"  • Invoices: {invoice_count:,}")
print(f"  • Order Items: {order_item_count:,}")

# Verify referential integrity
cursor.execute("""
    SELECT COUNT(*) FROM order_items oi 
    WHERE NOT EXISTS (SELECT 1 FROM invoices i WHERE i.invoice_id = oi.invoice_id)
""")
orphaned_orders = cursor.fetchone()[0]
print(f"\n✓ Data integrity check: {orphaned_orders} orphaned records found")

# Calculate total revenue
cursor.execute("SELECT SUM(total_amount) FROM invoices")
total_revenue = cursor.fetchone()[0]
print(f"✓ Total revenue: ${total_revenue:,.2f}")

print("\n" + "=" * 80)
print("DATA IMPORT & CLEANING COMPLETED SUCCESSFULLY!")
print("=" * 80)

# Close connection
cursor.close()
conn.close()
