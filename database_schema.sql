-- ============================================================================
-- E-COMMERCE DATABASE SCHEMA
-- ============================================================================
-- 
-- This SQL file defines the normalized database structure for the
-- e-commerce data analysis project. Execute this before running Python scripts.
--
-- Database: ecommerce_db
-- Tables: customers, products, invoices, order_items
-- Records: 400,916 transaction records from 4,312 customers
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- ============================================================================
-- TABLE 1: CUSTOMERS
-- ============================================================================
-- Stores unique customer information
-- Primary key: customer_id
-- 

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY COMMENT 'Unique customer identifier',
    country VARCHAR(50) COMMENT 'Customer country',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    INDEX idx_customer_id (customer_id) COMMENT 'PK lookup optimization',
    INDEX idx_customers_country (country) COMMENT 'Geographic query optimization'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Customer master table - 4,312 unique customers from 38 countries';

-- ============================================================================
-- TABLE 2: PRODUCTS
-- ============================================================================
-- Stores unique product information
-- Primary key: stock_code
--

CREATE TABLE IF NOT EXISTS products (
    stock_code VARCHAR(50) PRIMARY KEY COMMENT 'Unique product code',
    description VARCHAR(255) COMMENT 'Product name/description',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    INDEX idx_products_stock (stock_code) COMMENT 'Product lookup optimization'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Product catalog - 4,017 unique products';

-- ============================================================================
-- TABLE 3: INVOICES
-- ============================================================================
-- Stores invoice-level transaction information
-- Primary key: invoice_id
-- Foreign key: customer_id references customers(customer_id)
--

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(20) PRIMARY KEY COMMENT 'Unique invoice number',
    customer_id INT COMMENT 'Customer ID (foreign key)',
    invoice_date DATETIME COMMENT 'Date of transaction',
    total_amount DECIMAL(10, 2) COMMENT 'Total invoice amount in currency',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    
    CONSTRAINT fk_invoices_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    INDEX idx_invoice_customer (customer_id) COMMENT 'Customer-invoice join optimization',
    INDEX idx_invoice_date (invoice_date) COMMENT 'Time-series query optimization'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Invoice master table - 19,213 unique invoices';

-- ============================================================================
-- TABLE 4: ORDER_ITEMS
-- ============================================================================
-- Stores line-item details for each invoice
-- Primary key: order_item_id (auto-increment)
-- Foreign keys: invoice_id, stock_code
--

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique line item identifier',
    invoice_id VARCHAR(20) NOT NULL COMMENT 'Invoice reference (foreign key)',
    stock_code VARCHAR(50) NOT NULL COMMENT 'Product code (foreign key)',
    quantity INT COMMENT 'Quantity ordered',
    unit_price DECIMAL(10, 2) COMMENT 'Unit price at time of sale',
    line_total DECIMAL(12, 2) COMMENT 'Quantity * Unit_Price',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    
    CONSTRAINT fk_order_items_invoice FOREIGN KEY (invoice_id) 
        REFERENCES invoices(invoice_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    CONSTRAINT fk_order_items_product FOREIGN KEY (stock_code) 
        REFERENCES products(stock_code) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    INDEX idx_order_items_invoice (invoice_id) COMMENT 'Invoice detail lookup',
    INDEX idx_order_items_stock (stock_code) COMMENT 'Product lookup from items'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Order line items - 400,916 transaction records';

-- ============================================================================
-- DATABASE VIEWS (Optional - for common queries)
-- ============================================================================

-- ============================================================================
-- VIEW 1: CUSTOMER_RFM
-- ============================================================================
-- Calculate RFM metrics for each customer
--

CREATE OR REPLACE VIEW customer_rfm AS
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.country,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS recency,
        COUNT(DISTINCT i.invoice_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary,
        COUNT(DISTINCT i.invoice_id) / DATEDIFF('2011-12-09', MIN(i.invoice_date)) AS transaction_frequency
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    WHERE i.invoice_id IS NOT NULL
    GROUP BY c.customer_id, c.country
    HAVING monetary > 0
)
SELECT 
    customer_id,
    country,
    recency,
    frequency,
    monetary,
    NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(4) OVER (ORDER BY frequency) AS f_score,
    NTILE(4) OVER (ORDER BY monetary) AS m_score,
    CONCAT(
        NTILE(4) OVER (ORDER BY recency DESC),
        NTILE(4) OVER (ORDER BY frequency),
        NTILE(4) OVER (ORDER BY monetary)
    ) AS rfm_segment
FROM customer_stats;

-- ============================================================================
-- VIEW 2: PRODUCT_PERFORMANCE
-- ============================================================================
-- Analyze product sales metrics
--

CREATE OR REPLACE VIEW product_performance AS
SELECT 
    p.stock_code,
    p.description,
    COUNT(DISTINCT oi.invoice_id) AS num_sales,
    SUM(oi.quantity) AS total_quantity_sold,
    ROUND(AVG(oi.unit_price), 2) AS avg_price,
    ROUND(MIN(oi.unit_price), 2) AS min_price,
    ROUND(MAX(oi.unit_price), 2) AS max_price,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT oi.invoice_id), 2) AS avg_revenue_per_sale
FROM products p
LEFT JOIN order_items oi ON p.stock_code = oi.stock_code
GROUP BY p.stock_code, p.description;

-- ============================================================================
-- VIEW 3: GEOGRAPHIC_PERFORMANCE
-- ============================================================================
-- Analyze sales by country
--

CREATE OR REPLACE VIEW geographic_performance AS
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    COUNT(DISTINCT i.invoice_id) AS num_invoices,
    SUM(oi.quantity) AS total_items_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    ROUND(AVG(i.total_amount), 2) AS avg_invoice_amount,
    ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
LEFT JOIN invoices i ON c.customer_id = i.customer_id
LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
GROUP BY c.country
ORDER BY total_revenue DESC;

-- ============================================================================
-- STORED PROCEDURES (Optional - for common operations)
-- ============================================================================

-- ============================================================================
-- PROCEDURE 1: GET_CUSTOMER_DETAILS
-- ============================================================================
-- Retrieve comprehensive customer information
--

DELIMITER //

CREATE PROCEDURE IF NOT EXISTS get_customer_details(IN p_customer_id INT)
BEGIN
    SELECT 
        c.customer_id,
        c.country,
        COUNT(DISTINCT i.invoice_id) AS total_purchases,
        COUNT(DISTINCT oi.stock_code) AS unique_products,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_spent,
        ROUND(AVG(i.total_amount), 2) AS avg_purchase_amount,
        DATEDIFF('2011-12-09', MAX(i.invoice_date)) AS days_since_last_purchase,
        MIN(i.invoice_date) AS first_purchase_date,
        MAX(i.invoice_date) AS last_purchase_date
    FROM customers c
    LEFT JOIN invoices i ON c.customer_id = i.customer_id
    LEFT JOIN order_items oi ON i.invoice_id = oi.invoice_id
    WHERE c.customer_id = p_customer_id
    GROUP BY c.customer_id, c.country;
END //

DELIMITER ;

-- ============================================================================
-- PROCEDURE 2: GET_TOP_PRODUCTS
-- ============================================================================
-- Get top N products by revenue
--

DELIMITER //

CREATE PROCEDURE IF NOT EXISTS get_top_products(IN p_limit INT)
BEGIN
    SELECT 
        p.stock_code,
        p.description,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
        ROUND(AVG(oi.unit_price), 2) AS avg_price
    FROM products p
    LEFT JOIN order_items oi ON p.stock_code = oi.stock_code
    GROUP BY p.stock_code, p.description
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END //

DELIMITER ;

-- ============================================================================
-- INDEXES FOR QUERY OPTIMIZATION
-- ============================================================================
-- These indexes are created automatically during data import,
-- but listed here for reference

-- CREATE INDEX idx_customer_id ON customers(customer_id);
-- CREATE INDEX idx_customers_country ON customers(country);
-- CREATE INDEX idx_products_stock ON products(stock_code);
-- CREATE INDEX idx_invoice_customer ON invoices(customer_id);
-- CREATE INDEX idx_invoice_date ON invoices(invoice_date);
-- CREATE INDEX idx_order_items_invoice ON order_items(invoice_id);
-- CREATE INDEX idx_order_items_stock ON order_items(stock_code);

-- ============================================================================
-- DATA SUMMARY STATISTICS
-- ============================================================================
-- Expected record counts after successful import:
--
-- customers:     4,312 records
-- products:      4,017 records
-- invoices:     19,213 records
-- order_items: 400,916 records
--
-- Total Revenue: $8,798,233.73
-- Date Range: 2010-01-01 to 2011-12-09
-- Data Quality: 23.6% improvement after cleaning
--
-- ============================================================================

-- ============================================================================
-- END OF SCHEMA DEFINITION
-- ============================================================================
