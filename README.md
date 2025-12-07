# E-Commerce Data Analysis

Comprehensive e-commerce data analysis with SQL, Python, and interactive Plotly dashboard. Analyzed 525,000+ transactions to identify customer value patterns and business opportunities.

## 📊 Project Overview

This project demonstrates a complete data analytics pipeline from raw data to business insights:

- **Data Processing**: Cleaned 525K+ records (23.6% quality improvement)
- **Database Design**: Normalized schema with strategic indexing
- **Customer Analysis**: RFM segmentation identifying 5 customer tiers
- **Business Insights**: 80/20 rule, product performance, geographic opportunities
- **Interactive Dashboard**: 6 Plotly visualizations with real-time filtering

## 📈 Key Results

| Metric | Value |
|--------|-------|
| **Total Revenue** | $8.8M |
| **Customers Analyzed** | 4,312 |
| **Records Processed** | 400,916 |
| **Data Quality Improvement** | 23.6% |
| **Query Performance Gain** | 9.5% |

## 🛠 Tech Stack

- **Database**: MySQL 8.0.44
- **Programming**: Python 3.10
- **Libraries**: pandas, numpy, pymysql, plotly, openpyxl
- **Tools**: Git, SQL, Plotly

## 📁 Project Files

```
ecommerce-analysis/
├── README.md                      # This file
├── LICENSE                        # MIT License
├── database_schema.sql            # Database architecture
├── import_data.py                 # Data import & cleaning
├── rfm_analysis.py                # RFM customer segmentation
├── visualization_blue.py          # Dashboard generation
├── visualization_report_blue.html # Interactive dashboard
└── online_retail_II.xlsx          # Source data (525K records)
```

## 🚀 Quick Start (Step-by-Step)

### Step 1: Prerequisites

```bash
# Check Python version (3.10+)
python --version

# Check MySQL is running
mysql --version
```

**Requirements:**
- Python 3.10+
- MySQL 8.0+
- 200MB disk space

### Step 2: Download Data

Download the dataset from Kaggle:
- **Source**: [Online Retail II Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/online-retail-dataset)
- **File**: `online_retail_II.xlsx` (50-100MB)
- **Save to**: Project root directory

### Step 3: Install Python Dependencies

```bash
pip install pandas numpy pymysql plotly openpyxl
```

### Step 4: Setup MySQL Database

```bash
mysql -u root -p
```

Then run these commands:

```sql
CREATE DATABASE ecommerce_db;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'ecommerce_password';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5: Create Database Schema

```bash
mysql -u ecommerce_user -p ecommerce_db < database_schema.sql
# When prompted for password, enter: ecommerce_password
```

### Step 6: Import and Clean Data

```bash
python import_data.py
```

**Output:**
- Imports 525,461 raw records
- Removes invalid data (missing values, duplicates, negative quantities/prices)
- Creates 4 normalized tables with 7 indexes
- Final result: 400,916 valid transaction records

### Step 7: Run RFM Analysis

```bash
python rfm_analysis.py
```

**Output:**
- Calculates RFM metrics for each customer
- Segments customers into 5 value tiers
- Displays top customers and KPIs
- Performs 80/20 Pareto analysis

### Step 8: Generate Dashboard

```bash
python visualization_blue.py
```

**Output:**
- Generates `visualization_report_blue.html` (interactive dashboard)
- 6 Plotly charts with hover, zoom, pan, and download features
- File size: ~5-8MB

**Time:** ~2-5 minutes

### Step 9: View Results

Open the dashboard in your browser:

```bash
# Windows
start visualization_report_blue.html

# Mac
open visualization_report_blue.html

# Linux
xdg-open visualization_report_blue.html
```

---

## 📊 Interactive Dashboard

[View Dashboard](https://github.com/yukiii0818/Ecommerce-data-analysis/raw/master/visualization_report_blue.html)


## 📊 What You'll Find

### 1. Customer Segmentation

RFM (Recency, Frequency, Monetary) analysis identifies 5 customer tiers:

| Segment | Count | Avg Spending | Insight |
|---------|-------|--------------|---------|
| **Top-Tier** | 448 | $9,898 | VIP customers, highest value |
| **High-Value** | 831 | $2,306 | Active, frequent buyers |
| **Mid-Value** | 1,243 | $1,242 | Growing customer base |
| **At-Risk** | 787 | $260 | Inactive, needs attention |
| **Other** | 3 | $50+ | Edge cases |

**Key Finding**: Top 20% of customers generate **80% of revenue** (Pareto principle)

### 2. Product Performance

Top 5 products by revenue:
1. WHITE HANGING HEART T-LIGHT HOLDER - $153,379
2. REGENCY CAKESTAND 3 TIER - $117,780
3. MANUAL - $116,550
4. WORLD WAR 2 GLITTER FRAME - $107,667
5. JUMBO BAG RED RETROSPOT - $99,993

**Key Finding**: Top 20% of products = 78% of revenue

### 3. Geographic Distribution

Top 5 countries:
1. United Kingdom - $6,584,950 (74.8%)
2. Netherlands - $286,222 (3.3%)
3. Ireland - $268,788 (3.1%)
4. Germany - $227,639 (2.6%)
5. France - $206,555 (2.3%)

**Key Finding**: Heavy UK concentration with 20% EU opportunity for expansion

### 4. Sales Patterns

- **Peak**: October-November (holiday season, 20-30% above average)
- **Low**: January-February (post-holiday)
- **Average**: ~$733K monthly revenue
- **Pattern**: Clear seasonal cycles enable forecasting

### 5. Interactive Dashboard

**6 Visualizations**:
1. Customer Value Segmentation (RFM scatter plot)
2. Top 15 Products (revenue bar chart)
3. Geographic Distribution (revenue by country pie chart)
4. Monthly Sales Trend (seasonal line chart)
5. Product Performance (price vs volume scatter)
6. Customer LTV Distribution (lifetime value histogram)

**Interactive Features**:
- ✨ Hover for detailed metrics
- 📍 Zoom and pan capability
- 📊 Click legend to filter
- 💾 Download charts as PNG
- 📱 Responsive on all devices

---

## 💡 Business Insights & Recommendations

### Customer Insights

✅ **Top 20% customers drive 80% revenue** - Focus retention and VIP programs

✅ **4,312 customers total** - Mid-size customer base with concentration risk

✅ **Average LTV: $2,040** - Good baseline for marketing spend optimization

### Product Insights

✅ **Long-tail product mix** - Few bestsellers, many low-volume products

✅ **Home décor dominance** - Product category focus area

✅ **Bundle opportunity** - Pair slow-moving with bestselling products

### Market Insights

✅ **UK market over-concentrated** - 74.8% revenue from single country

✅ **EU expansion potential** - 20% of revenue from EU (3.3-3.1% each)

✅ **38 countries served** - Global reach but needs regional focus

### Operational Insights

✅ **Strong seasonality** - Q4 peaks, Q1 dips (predictable patterns)

✅ **Inventory planning** - Use seasonal trends for stock optimization

✅ **Forecasting ready** - Historical patterns enable demand prediction

---

## 📊 Database Architecture

### Tables (4 total, 400K+ records)

**customers** (4,312 records)
- customer_id: Unique customer identifier
- country: Customer location
- Indexes: PK, country

**products** (4,017 records)
- stock_code: Unique product identifier
- description: Product name
- Indexes: PK

**invoices** (19,213 records)
- invoice_id: Transaction ID
- customer_id: Foreign key to customers
- invoice_date: Transaction date
- total_amount: Invoice total
- Indexes: customer_id, invoice_date

**order_items** (400,916 records)
- order_item_id: Line item ID
- invoice_id: Foreign key to invoices
- stock_code: Foreign key to products
- quantity: Units ordered
- unit_price: Price per unit
- line_total: Quantity × Price
- Indexes: invoice_id, stock_code

### Performance

- **7 strategic indexes** created for optimal query performance
- **9.5% query improvement** achieved through indexing
- **3 analytical views** for common business queries
- **2 stored procedures** for frequent operations

---

## 🔧 Troubleshooting

### Issue: "MySQL connection failed"

**Solution:**
1. Verify MySQL is running: `mysql -u root -p`
2. Check credentials: `ecommerce_user` / `ecommerce_password`
3. Verify database exists: `SHOW DATABASES;`

### Issue: "File not found: online_retail_II.xlsx"

**Solution:**
1. Download from Kaggle
2. Place in project root directory
3. Verify filename matches exactly

### Issue: "Python module not found"

**Solution:**
```bash
pip install pandas numpy pymysql plotly openpyxl --upgrade
```

### Issue: "HTML file won't open"

**Solution:**
1. Use modern browser (Chrome, Firefox, Edge, Safari)
2. Open directly from file system or local server
3. Check file size (should be ~5-8MB)

### Issue: "Script runs but no output"

**Solution:**
1. Check MySQL connection is working
2. Verify data was imported (`SELECT COUNT(*) FROM order_items;`)
3. Check disk space available

---

## 📝 Data Processing Pipeline

### Import Stage (import_data.py)

1. **Load** 525,461 records from Excel
2. **Clean** data in 7 steps:
   - Remove missing Customer ID/Description: -114,727 rows
   - Remove duplicates: -8,671 rows
   - Remove invalid quantities (≤0): -41,047 rows
   - Remove invalid prices (≤0): -5,025 rows
3. **Create** 4 normalized tables
4. **Index** with 7 strategic indexes
5. **Verify** data integrity
6. **Result**: 400,916 valid records (23.6% improvement)

### Analysis Stage (rfm_analysis.py)

1. **Calculate** RFM metrics (Recency, Frequency, Monetary)
2. **Score** customers using NTILE (1-4 scale)
3. **Segment** into 5 tiers (Top-Tier, High-Value, Mid-Value, At-Risk, Other)
4. **Analyze** top customers and products
5. **Calculate** KPIs (avg LTV, total revenue, etc.)
6. **Perform** 80/20 Pareto analysis

### Visualization Stage (visualization_blue.py)

1. **Query** aggregated data from database
2. **Create** 6 Plotly visualizations
3. **Style** with professional blue theme
4. **Add** KPI summary cards
5. **Generate** interactive HTML dashboard
6. **Output**: visualization_report_blue.html

---

## 👤 Author

**Yuki** (yukiii0818)
- GitHub: https://github.com/yukiii0818/
- Email: yukiii0818@163.com

---

## 🙏 Acknowledgments

- Data source: [Online Retail II (Kaggle)](https://www.kaggle.com/datasets/lakshmi25npathi/online-retail-dataset)
- Tools: MySQL, Python, Plotly, pandas
- Technologies: SQL, database design, Python data processing

---

**Last Updated**: December 2024  
**Data Period**: 2010-2011  
**Status**: Complete & Ready to Use
