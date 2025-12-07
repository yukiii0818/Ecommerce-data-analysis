import pandas as pd
import pymysql

# Connect to MySQL
conn = pymysql.connect(
    host='localhost',
    user='ecommerce_user',
    password='ecommerce_password',
    database='ecommerce_db'
)
cursor = conn.cursor()

print("=" * 100)
print("RFM CUSTOMER ANALYSIS & SEGMENTATION")
print("=" * 100)

# ============================================================================
# STEP 1: Calculate RFM values for each customer
# ============================================================================

print("\n[STEP 1] Calculating RFM values for each customer...\n")

rfm_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.country,
        DATEDIFF(MAX(i.invoice_date), MIN(i.invoice_date)) AS days_active,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id, c.country
    HAVING monetary > 0
)
SELECT * FROM customer_rfm
ORDER BY monetary DESC
LIMIT 20;
"""

cursor.execute(rfm_query)
rfm_data = cursor.fetchall()
print("Top 20 customers by RFM metrics:")
print(f"{'Customer ID':<12} {'Country':<15} {'Days Active':<12} {'Recency':<10} {'Frequency':<12} {'Monetary':<15}")
print("-" * 80)
for row in rfm_data:
    print(f"{row[0]:<12.0f} {row[1]:<15} {row[2]:<12} {row[3]:<10} {row[4]:<12} ${row[5]:<14.2f}")

# ============================================================================
# STEP 2: RFM Scoring (1-4 scale)
# ============================================================================

print("\n" + "=" * 100)
print("[STEP 2] Scoring RFM values using NTILE partitioning (1-4 scale)...\n")

rfm_segment_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.country,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id, c.country
    HAVING monetary > 0
),
rfm_scores AS (
    SELECT 
        customer_id,
        country,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency) AS f_score,
        NTILE(4) OVER (ORDER BY monetary) AS m_score
    FROM customer_rfm
)
SELECT 
    customer_id,
    country,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score) AS rfm_segment
FROM rfm_scores
ORDER BY monetary DESC
LIMIT 20;
"""

cursor.execute(rfm_segment_query)
rfm_segment_data = cursor.fetchall()
print("Top 20 customers with RFM scores:")
print(f"{'Customer':<10} {'Recency':<10} {'Freq':<6} {'Monetary':<12} {'R':<3} {'F':<3} {'M':<3} {'Segment':<10}")
print("-" * 70)
for row in rfm_segment_data:
    print(f"{row[0]:<10.0f} {row[2]:<10} {row[3]:<6} ${row[4]:<11.2f} {row[5]:<3} {row[6]:<3} {row[7]:<3} {row[8]:<10}")

# ============================================================================
# STEP 3: Customer Segmentation
# ============================================================================

print("\n" + "=" * 100)
print("[STEP 3] Customer segmentation by value tier...\n")

customer_segment_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.country,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id, c.country
    HAVING monetary > 0
),
rfm_scores AS (
    SELECT 
        customer_id,
        country,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency) AS f_score,
        NTILE(4) OVER (ORDER BY monetary) AS m_score
    FROM customer_rfm
),
customer_segments AS (
    SELECT 
        customer_id,
        country,
        recency,
        frequency,
        monetary,
        CONCAT(r_score, f_score, m_score) AS rfm_segment,
        CASE 
            WHEN r_score = 4 AND f_score = 4 AND m_score = 4 THEN 'Top-Tier'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'High-Value'
            WHEN r_score >= 2 AND f_score >= 2 AND m_score >= 2 THEN 'Mid-Value'
            WHEN r_score = 1 AND f_score <= 2 AND m_score <= 2 THEN 'At-Risk'
            ELSE 'Other'
        END AS segment
    FROM rfm_scores
)
SELECT segment, COUNT(*) AS count, ROUND(AVG(monetary), 2) AS avg_monetary
FROM customer_segments
GROUP BY segment
ORDER BY avg_monetary DESC;
"""

cursor.execute(customer_segment_query)
segment_data = cursor.fetchall()
print("Customer segmentation summary:")
print(f"{'Segment':<15} {'Count':<10} {'Avg Monetary':<20}")
print("-" * 50)
for row in segment_data:
    print(f"{row[0]:<15} {row[1]:<10} ${row[2]:<19.2f}")

# ============================================================================
# STEP 4: Top-Tier & High-Value Customers
# ============================================================================

print("\n" + "=" * 100)
print("[STEP 4] Detailed analysis of top-tier and high-value customers...\n")

top_customers_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.country,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id, c.country
    HAVING monetary > 0
),
rfm_scores AS (
    SELECT 
        customer_id,
        country,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency) AS f_score,
        NTILE(4) OVER (ORDER BY monetary) AS m_score
    FROM customer_rfm
)
SELECT 
    customer_id,
    country,
    recency,
    frequency,
    monetary,
    CASE 
        WHEN r_score = 4 AND f_score = 4 AND m_score = 4 THEN 'Top-Tier'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'High-Value'
    END AS customer_tier
FROM rfm_scores
WHERE (r_score = 4 AND f_score = 4 AND m_score = 4) 
   OR (r_score >= 3 AND f_score >= 3 AND m_score >= 3)
ORDER BY monetary DESC
LIMIT 20;
"""

cursor.execute(top_customers_query)
top_customers = cursor.fetchall()
print("Top-tier and high-value customers (top 20):")
print(f"{'Customer ID':<12} {'Country':<15} {'Recency':<10} {'Frequency':<12} {'Monetary':<15} {'Tier':<12}")
print("-" * 80)
for row in top_customers:
    tier = row[5] if row[5] else "N/A"
    print(f"{row[0]:<12.0f} {row[1]:<15} {row[2]:<10} {row[3]:<12} ${row[4]:<14.2f} {tier:<12}")

# ============================================================================
# STEP 5: Key Performance Indicators (KPIs)
# ============================================================================

print("\n" + "=" * 100)
print("[STEP 5] Key Performance Indicators (KPIs)...\n")

kpi_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id
    HAVING monetary > 0
)
SELECT 
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(AVG(frequency), 2) AS avg_purchase_frequency,
    ROUND(AVG(monetary), 2) AS avg_customer_ltv,
    ROUND(SUM(monetary), 2) AS total_revenue,
    MAX(monetary) AS top_customer_spending,
    MIN(monetary) AS min_customer_spending
FROM customer_rfm;
"""

cursor.execute(kpi_query)
kpi_data = cursor.fetchone()
print("Key Business Metrics:")
print(f"  • Total Customers: {kpi_data[0]:,}")
print(f"  • Average Purchase Frequency: {kpi_data[1]:.2f} transactions")
print(f"  • Average Customer LTV (Lifetime Value): ${kpi_data[2]:.2f}")
print(f"  • Total Revenue: ${kpi_data[3]:,.2f}")
print(f"  • Highest Customer Spending: ${kpi_data[4]:,.2f}")
print(f"  • Lowest Customer Spending: ${kpi_data[5]:.2f}")

# ============================================================================
# STEP 6: 80/20 Analysis (Pareto Principle)
# ============================================================================

print("\n" + "=" * 100)
print("[STEP 6] 80/20 Pareto Analysis (top customers vs total revenue)...\n")

pareto_query = """
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    GROUP BY c.customer_id
    HAVING monetary > 0
),
total_stats AS (
    SELECT 
        COUNT(*) AS total_customers,
        SUM(monetary) AS total_revenue
    FROM customer_rfm
),
top_20_percent AS (
    SELECT 
        COUNT(*) AS top_customers,
        SUM(monetary) AS top_revenue
    FROM (
        SELECT customer_id, monetary
        FROM customer_rfm
        ORDER BY monetary DESC
        LIMIT (SELECT CEIL(COUNT(*) * 0.2) FROM customer_rfm)
    ) t
)
SELECT 
    ts.total_customers,
    ts.total_revenue,
    t2.top_customers,
    t2.top_revenue,
    ROUND((t2.top_customers / ts.total_customers) * 100, 1) AS top_pct_of_customers,
    ROUND((t2.top_revenue / ts.total_revenue) * 100, 1) AS top_pct_of_revenue
FROM total_stats ts, top_20_percent t2;
"""

cursor.execute(pareto_query)
pareto_data = cursor.fetchone()
print("Pareto Analysis Results:")
print(f"  • Total Customers: {pareto_data[0]:,}")
print(f"  • Total Revenue: ${pareto_data[1]:,.2f}")
print(f"  • Top 20% Customers Count: {pareto_data[2]:,}")
print(f"  • Top 20% Customers Revenue: ${pareto_data[3]:,.2f}")
print(f"  • Top 20% represents {pareto_data[4]:.1f}% of customer base")
print(f"  • Top 20% generates {pareto_data[5]:.1f}% of total revenue")

print("\n" + "=" * 100)
print("RFM ANALYSIS COMPLETED SUCCESSFULLY!")
print("=" * 100)

# Close connection
cursor.close()
conn.close()
