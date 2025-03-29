DROP TABLE IF EXISTS customer_segments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- Create customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(50),
    first_purchase_date DATE,
    last_purchase_date DATE,
    total_purchases INT DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0.00
);

-- Create products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    description TEXT,
    unit_price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    stock_code VARCHAR(50) NOT NULL
);

-- Create orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_date TIMESTAMP NOT NULL,
    country VARCHAR(50),
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create order_items table
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create customer_segments table (for RFM analysis results)
CREATE TABLE customer_segments (
    customer_id VARCHAR(50) PRIMARY KEY,
    recency_score INT,
    frequency_score INT,
    monetary_score INT,
    rfm_score INT,
    segment VARCHAR(50),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_customer_segments_segment ON customer_segments(segment);

-- Create a simple log table to track data processing steps
CREATE TABLE data_processing_log (
    log_id SERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    records_processed INT,
    status VARCHAR(50),
    error_message TEXT
);