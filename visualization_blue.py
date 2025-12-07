import pymysql
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Connect to MySQL
conn = pymysql.connect(
    host='localhost',
    user='ecommerce_user',
    password='ecommerce_password',
    database='ecommerce_db'
)

print("=" * 80)
print("GENERATING VERSION A: CORPORATE BLUE PROFESSIONAL DASHBOARD")
print("=" * 80)

# ============================================================================
# 1. RFM Customer Segmentation
# ============================================================================

print("\n[1/6] Generating RFM scatter plot...")

rfm_query = """
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
),
rfm_scores AS (
    SELECT 
        customer_id,
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
        recency,
        frequency,
        monetary,
        CASE 
            WHEN r_score = 4 AND f_score = 4 AND m_score = 4 THEN 'Top-Tier'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'High-Value'
            WHEN r_score >= 2 AND f_score >= 2 AND m_score >= 2 THEN 'Mid-Value'
            WHEN r_score = 1 AND f_score <= 2 AND m_score <= 2 THEN 'At-Risk'
            ELSE 'Other'
        END AS segment
    FROM rfm_scores
)
SELECT * FROM customer_segments;
"""

rfm_df = pd.read_sql(rfm_query, conn)

fig_rfm = px.scatter(
    rfm_df,
    x='frequency',
    y='monetary',
    size='recency',
    color='segment',
    hover_name='customer_id',
    hover_data={'customer_id': ':.0f', 'recency': ':.0f', 'frequency': ':.0f', 'monetary': ':.2f', 'segment': True},
    title='Customer Lifetime Value by Purchase Frequency',
    labels={'frequency': 'Purchase Frequency', 'monetary': 'Total Spending ($)', 'segment': 'Segment'},
    color_discrete_map={
        'Top-Tier': '#003f87',
        'High-Value': '#0066cc',
        'Mid-Value': '#3399ff',
        'At-Risk': '#cccccc',
        'Other': '#e6e6e6'
    }
)

fig_rfm.update_layout(
    height=600,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=11, color="#333333"),
    hovermode='closest',
    showlegend=True,
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=80, r=40, t=60, b=60),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#e6e6e6', showgrid=True),
    yaxis=dict(gridcolor='#e6e6e6', showgrid=True)
)

fig_rfm.update_traces(marker=dict(line=dict(width=0.5, color='white')))

# ============================================================================
# 2. Top 15 Products by Revenue
# ============================================================================

print("[2/6] Generating top products chart...")

products_query = """
SELECT 
    p.description,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.stock_code = p.stock_code
GROUP BY p.stock_code, p.description
ORDER BY total_revenue DESC
LIMIT 15;
"""

products_df = pd.read_sql(products_query, conn)

fig_products = px.bar(
    products_df.sort_values('total_revenue'),
    y='description',
    x='total_revenue',
    orientation='h',
    title='Revenue by Product (Top 15)',
    labels={'total_revenue': 'Revenue ($)', 'description': ''},
    color='total_revenue',
    color_continuous_scale=['#b3d9ff', '#0066cc']
)

fig_products.update_layout(
    height=500,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=10, color="#333333"),
    showlegend=False,
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=250, r=40, t=60, b=40),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#e6e6e6', showgrid=True),
    yaxis=dict(showgrid=False)
)

fig_products.update_traces(marker_color='#0066cc', marker_line=dict(width=0))

# ============================================================================
# 3. Sales by Country
# ============================================================================

print("[3/6] Generating geographic chart...")

country_query = """
SELECT 
    c.country,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    COUNT(DISTINCT c.customer_id) AS customer_count
FROM customers c
JOIN invoices i ON c.customer_id = i.customer_id
JOIN order_items oi ON i.invoice_id = oi.invoice_id
GROUP BY c.country
ORDER BY total_revenue DESC
LIMIT 15;
"""

country_df = pd.read_sql(country_query, conn)

fig_country = px.pie(
    country_df,
    names='country',
    values='total_revenue',
    title='Revenue Distribution by Country (Top 15)',
    hover_data={'customer_count': True, 'total_revenue': ':$,.0f'}
)

fig_country.update_layout(
    height=600,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=11, color="#333333"),
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=20, r=20, t=60, b=20),
    paper_bgcolor='white'
)

fig_country.update_traces(
    textposition='inside',
    textinfo='label+percent',
    marker=dict(line=dict(color='white', width=2))
)

# ============================================================================
# 4. Monthly Sales Trend
# ============================================================================

print("[4/6] Generating monthly trend chart...")

monthly_query = """
SELECT 
    DATE_FORMAT(i.invoice_date, '%Y-%m') AS month,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monthly_revenue
FROM invoices i
JOIN order_items oi ON i.invoice_id = oi.invoice_id
GROUP BY DATE_FORMAT(i.invoice_date, '%Y-%m')
ORDER BY month;
"""

monthly_df = pd.read_sql(monthly_query, conn)

fig_monthly = px.line(
    monthly_df,
    x='month',
    y='monthly_revenue',
    title='Monthly Revenue Trend',
    labels={'month': 'Month', 'monthly_revenue': 'Revenue ($)'},
    markers=True
)

fig_monthly.update_layout(
    height=500,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=11, color="#333333"),
    hovermode='x unified',
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=80, r=40, t=60, b=60),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#e6e6e6', showgrid=True),
    yaxis=dict(gridcolor='#e6e6e6', showgrid=True)
)

fig_monthly.update_traces(
    line=dict(color='#0066cc', width=3),
    marker=dict(size=6, color='#003f87')
)

# ============================================================================
# 5. Product Price vs Sales Volume
# ============================================================================

print("[5/6] Generating price-volume scatter plot...")

price_query = """
SELECT 
    p.description,
    ROUND(AVG(oi.unit_price), 2) AS avg_price,
    SUM(oi.quantity) AS quantity_sold
FROM order_items oi
JOIN products p ON oi.stock_code = p.stock_code
GROUP BY p.stock_code, p.description
ORDER BY quantity_sold DESC
LIMIT 20;
"""

price_df = pd.read_sql(price_query, conn)

fig_price = px.scatter(
    price_df,
    x='avg_price',
    y='quantity_sold',
    size='quantity_sold',
    hover_name='description',
    title='Product Performance: Price vs Sales Volume',
    labels={'avg_price': 'Average Price ($)', 'quantity_sold': 'Units Sold'},
    color='avg_price',
    color_continuous_scale=['#87ceeb', '#003f87']
)

fig_price.update_layout(
    height=600,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=11, color="#333333"),
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=80, r=40, t=60, b=60),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#e6e6e6', showgrid=True),
    yaxis=dict(gridcolor='#e6e6e6', showgrid=True),
    hovermode='closest'
)

fig_price.update_traces(marker=dict(line=dict(width=0.5, color='white')))

# ============================================================================
# 6. Customer LTV Distribution
# ============================================================================

print("[6/6] Generating LTV distribution chart...")

ltv_query = """
SELECT 
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS customer_ltv
FROM customers c
LEFT JOIN invoices i ON c.customer_id = i.customer_id
LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
WHERE c.customer_id IS NOT NULL
GROUP BY c.customer_id
HAVING customer_ltv > 0;
"""

ltv_df = pd.read_sql(ltv_query, conn)

fig_ltv = px.histogram(
    ltv_df,
    x='customer_ltv',
    nbins=50,
    title='Customer Lifetime Value Distribution',
    labels={'customer_ltv': 'Customer LTV ($)'},
    color_discrete_sequence=['#0066cc']
)

fig_ltv.update_layout(
    height=500,
    template='plotly_white',
    font=dict(family="Segoe UI, Arial", size=11, color="#333333"),
    title_font_size=16,
    title_x=0.0,
    margin=dict(l=80, r=40, t=60, b=60),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#e6e6e6', showgrid=True, title_text='Customer LTV ($)'),
    yaxis=dict(gridcolor='#e6e6e6', showgrid=True, title_text='Number of Customers'),
    showlegend=False
)

fig_ltv.update_traces(marker_line=dict(color='white', width=1))

# ============================================================================
# Generate HTML Dashboard
# ============================================================================

print("\nCombining charts into professional dashboard...")

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            color: #333333;
        }}
        
        .dashboard-header {{
            background: linear-gradient(135deg, #003f87 0%, #0066cc 100%);
            color: white;
            padding: 40px 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-bottom: 4px solid #003f87;
        }}
        
        .dashboard-header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .dashboard-header p {{
            font-size: 13px;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .kpi-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            padding: 20px 30px;
            background-color: white;
            border-bottom: 1px solid #e6e6e6;
        }}
        
        .kpi-card {{
            background: white;
            border-left: 4px solid #0066cc;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.12);
        }}
        
        .kpi-value {{
            font-size: 24px;
            font-weight: bold;
            color: #003f87;
            margin: 10px 0;
        }}
        
        .kpi-label {{
            font-size: 12px;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            padding: 20px;
            border-top: 3px solid #0066cc;
        }}
        
        .chart-container.full-width {{
            grid-column: 1 / -1;
        }}
        
        .chart-title {{
            font-size: 14px;
            font-weight: 600;
            color: #333333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .chart-description {{
            font-size: 12px;
            color: #888888;
            margin-bottom: 15px;
            font-style: italic;
        }}
        
        .dashboard-footer {{
            text-align: center;
            padding: 20px 30px;
            color: #999999;
            font-size: 11px;
            border-top: 1px solid #e6e6e6;
            background: white;
            margin-top: 30px;
            border-radius: 4px;
        }}
        
        @media (max-width: 1200px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .print-notice {{
            font-size: 11px;
            color: #666666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>📊 E-Commerce Analytics Dashboard</h1>
        <p>Data Period: January 2010 - December 2011 | Interactive Analysis Report</p>
        <div class="print-notice">💡 Tip: Use browser print (Ctrl+P or Cmd+P) to save as PDF</div>
    </div>
    
    <div class="kpi-section">
        <div class="kpi-card">
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-value">4,312</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Transactions</div>
            <div class="kpi-value">19,213</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">$8.8M</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg. Customer LTV</div>
            <div class="kpi-value">$2,040</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Unique Products</div>
            <div class="kpi-value">4,017</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Countries Served</div>
            <div class="kpi-value">38</div>
        </div>
    </div>
    
    <div class="container">
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">Customer Value Analysis</div>
                <div class="chart-description">RFM segmentation by purchase frequency and lifetime spending</div>
                <div id="chart1"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Top Revenue Products</div>
                <div class="chart-description">Leading products ranked by total revenue contribution</div>
                <div id="chart2"></div>
            </div>
            
            <div class="chart-container full-width">
                <div class="chart-title">Geographic Performance</div>
                <div class="chart-description">Revenue distribution across 38 countries - top 15 shown</div>
                <div id="chart3"></div>
            </div>
            
            <div class="chart-container full-width">
                <div class="chart-title">Sales Trend Analysis</div>
                <div class="chart-description">Monthly revenue pattern showing seasonality and growth trends</div>
                <div id="chart4"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Product Performance Matrix</div>
                <div class="chart-description">Price positioning against sales volume (top 20 products)</div>
                <div id="chart5"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Customer Value Distribution</div>
                <div class="chart-description">Histogram of customer lifetime value (LTV) across all customers</div>
                <div id="chart6"></div>
            </div>
        </div>
    </div>
    
    <div class="dashboard-footer">
        <p>© E-Commerce Data Analysis Project | Generated: December 2024</p>
        <p>Database: MySQL | Analysis: Python (pandas, plotly) | Data Quality: 23.6% improvement after cleaning</p>
        <p>Interactive Features: Hover for details • Zoom • Pan • Click legend to toggle • Download chart</p>
    </div>
    
    <script>
        const charts = [
            {fig_rfm.to_json()},
            {fig_products.to_json()},
            {fig_country.to_json()},
            {fig_monthly.to_json()},
            {fig_price.to_json()},
            {fig_ltv.to_json()}
        ];
        
        const chartDivs = ['chart1', 'chart2', 'chart3', 'chart4', 'chart5', 'chart6'];
        
        for (let i = 0; i < charts.length; i++) {{
            Plotly.newPlot(chartDivs[i], charts[i].data, charts[i].layout, {{
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['toImage']
            }});
        }}
    </script>
</body>
</html>
"""

with open('visualization_report_v1_corporate_blue.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n" + "=" * 80)
print("✓ VERSION A COMPLETED!")
print("=" * 80)
print("\nOutput: visualization_report_v1_corporate_blue.html")
print("\nStyle: Corporate Blue (Professional Business)")
print("  • Color: Traditional corporate blue (#003f87, #0066cc)")
print("  • Font: Segoe UI, professional sans-serif")
print("  • Layout: Clean grid with borders and shadows")
print("  • Best for: Traditional business, finance, enterprise")

conn.close()
