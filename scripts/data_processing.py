"""
Data Processing Module - Optimized for UCI Online Retail Dataset

This module handles the cleaning and transformation of raw e-commerce data.
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import re
from scripts.db_utils import connect_to_database, execute_many

logger = logging.getLogger(__name__)

def clean_online_retail_data(df):
    """
    Clean the raw Online Retail dataset.
    
    Args:
        df: Raw pandas DataFrame
        
    Returns:
        Cleaned pandas DataFrame
    """
    logger.info("Starting data cleaning process")
    initial_rows = len(df)
    
    # Make a copy to avoid modifying original data
    df_clean = df.copy()
    
    # Log the actual columns for debugging
    logger.info(f"Actual columns in dataframe: {list(df_clean.columns)}")
    
    # Convert data types for UCI Online Retail dataset
    if 'InvoiceDate' in df_clean.columns:
        df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], errors='coerce')
    
    # Handle missing values
    logger.info(f"Missing values before cleaning: {df_clean.isnull().sum().sum()}")
    
    # Remove rows with missing CustomerID
    if 'CustomerID' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['CustomerID'])
        # Convert CustomerID to string type
        df_clean['CustomerID'] = df_clean['CustomerID'].astype(str)
    
    # Remove rows with missing InvoiceNo
    if 'InvoiceNo' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['InvoiceNo'])
        # Convert InvoiceNo to string type
        df_clean['InvoiceNo'] = df_clean['InvoiceNo'].astype(str)
        
        # Handle cancelled orders (invoices starting with 'C')
        if df_clean['InvoiceNo'].str.startswith('C').any():
            df_clean = df_clean[~df_clean['InvoiceNo'].str.startswith('C')]
    
    # Remove rows with non-positive quantities or prices
    if 'Quantity' in df_clean.columns and 'UnitPrice' in df_clean.columns:
        df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
        
        # Calculate total price
        df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']
    
    # Handle missing descriptions
    if 'Description' in df_clean.columns:
        df_clean['Description'].fillna('Unknown', inplace=True)
    
    # Remove outliers if we have the necessary columns
    if 'UnitPrice' in df_clean.columns and 'Quantity' in df_clean.columns:
        price_mean = df_clean['UnitPrice'].mean()
        price_std = df_clean['UnitPrice'].std()
        quantity_mean = df_clean['Quantity'].mean()
        quantity_std = df_clean['Quantity'].std()
        
        df_clean = df_clean[
            (df_clean['UnitPrice'] < price_mean + 3*price_std) &
            (df_clean['Quantity'] < quantity_mean + 3*quantity_std)
        ]
    
    # Log cleaning results
    final_rows = len(df_clean)
    logger.info(f"Rows before cleaning: {initial_rows}")
    logger.info(f"Rows after cleaning: {final_rows}")
    logger.info(f"Removed {initial_rows - final_rows} rows ({(initial_rows - final_rows) / initial_rows:.2%})")
    logger.info(f"Missing values after cleaning: {df_clean.isnull().sum().sum()}")
    
    return df_clean

def extract_product_categories(df):
    """
    Extract product categories from descriptions.
    
    Args:
        df: Cleaned pandas DataFrame
        
    Returns:
        DataFrame with extracted categories
    """
    logger.info("Extracting product categories")
    
    # Make a copy to avoid modifying original data
    df_with_categories = df.copy()
    
    # Simple category extraction based on common keywords in descriptions
    category_patterns = {
        'Gift': r'gift|set|box|christmas|holiday',
        'Kitchen': r'kitchen|cook|bake|spoon|fork|knife|plate|cup|kettle|jar|bottle',
        'Garden': r'garden|outdoor|plant|flower|seed',
        'Decoration': r'decor|decoration|ornament|candle|frame|sign|holder',
        'Storage': r'box|bag|storage|basket|tin|case',
        'Bathroom': r'bath|shower|soap|towel',
        'Clothing': r'bag|hat|scarf|shirt|cloth',
        'Toys': r'toy|game|play|puzzle',
        'Stationery': r'paper|card|pen|pencil|tape|notebook',
        'Food': r'coffee|tea|chocolate|cake|food|drink'
    }
    
    # Create a function to determine category
    def determine_category(desc):
        if pd.isna(desc) or desc == 'Unknown':
            return 'Unknown'
        
        desc_lower = str(desc).lower()
        
        for category, pattern in category_patterns.items():
            if re.search(pattern, desc_lower):
                return category
        
        return 'Other'
    
    # Apply the function to extract categories for UCI Online Retail dataset
    if 'Description' in df_with_categories.columns:
        df_with_categories['Category'] = df_with_categories['Description'].apply(determine_category)
        
        # Log category distribution
        category_counts = df_with_categories['Category'].value_counts()
        logger.info(f"Extracted {len(category_counts)} product categories")
        logger.info(f"Category distribution:\n{category_counts}")
    else:
        logger.warning("Description column not found in dataframe")
        # Add a default category
        df_with_categories['Category'] = 'Unknown'
    
    return df_with_categories

def transform_to_relational_model(df):
    """
    Transform the flat UCI Online Retail dataset into a relational model.
    
    Args:
        df: Cleaned pandas DataFrame with categories
        
    Returns:
        Dictionary of DataFrames for each entity (customers, products, orders, order_items)
    """
    logger.info("Transforming UCI Online Retail data to relational model")
    
    # Extract customers - using the actual column names from UCI dataset
    customers = df.groupby('CustomerID').agg(
        Country=('Country', 'first'),
        FirstPurchase=('InvoiceDate', 'min'),
        LastPurchase=('InvoiceDate', 'max'),
        TotalPurchases=('InvoiceNo', lambda x: x.nunique()),
        TotalSpent=('TotalPrice', 'sum')
    ).reset_index()
    
    # Convert date columns to datetime to ensure consistent types
    customers['FirstPurchase'] = pd.to_datetime(customers['FirstPurchase']).dt.date
    customers['LastPurchase'] = pd.to_datetime(customers['LastPurchase']).dt.date
    
    # Rename columns to match database schema
    customers.columns = ['customer_id', 'country', 'first_purchase_date', 
                        'last_purchase_date', 'total_purchases', 'total_spent']
    
    # Extract products (unique StockCode, Description, Category combinations)
    products = df.drop_duplicates(subset=['StockCode']).copy()
    products['product_id'] = 'P' + products['StockCode'].astype(str)
    products = products[['product_id', 'Description', 'UnitPrice', 'Category', 'StockCode']]
    products.columns = ['product_id', 'description', 'unit_price', 'category', 'stock_code']
    
    # Extract orders (invoice level data)
    orders = df.groupby(['InvoiceNo', 'CustomerID', 'InvoiceDate', 'Country']).agg(
        TotalAmount=('TotalPrice', 'sum')
    ).reset_index()
    
    orders.columns = ['order_id', 'customer_id', 'order_date', 'country', 'total_amount']
    
    # Create order items
    order_items = df.copy()
    order_items['product_id'] = 'P' + order_items['StockCode'].astype(str)
    order_items = order_items[['InvoiceNo', 'product_id', 'Quantity', 'UnitPrice', 'TotalPrice']]
    order_items.columns = ['order_id', 'product_id', 'quantity', 'unit_price', 'total_price']
    
    # Log entity counts
    logger.info(f"Created {len(customers)} customer records")
    logger.info(f"Created {len(products)} product records")
    logger.info(f"Created {len(orders)} order records")
    logger.info(f"Created {len(order_items)} order item records")
    
    return {
        'customers': customers,
        'products': products,
        'orders': orders,
        'order_items': order_items
    }

def save_processed_data(data_dict, output_dir):
    """
    Save processed data to CSV files.
    
    Args:
        data_dict: Dictionary of DataFrames for each entity
        output_dir: Directory to save the processed data
        
    Returns:
        Dictionary of paths to the saved files
    """
    logger.info(f"Saving processed data to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    file_paths = {}
    
    for entity_name, df in data_dict.items():
        file_path = os.path.join(output_dir, f"{entity_name}.csv")
        df.to_csv(file_path, index=False)
        file_paths[entity_name] = file_path
        logger.info(f"Saved {entity_name} data to {file_path}")
    
    return file_paths

def load_data_to_database(data_dict, db_config):
    """
    Load the processed data into the database.
    
    Args:
        data_dict: Dictionary of DataFrames for each entity
        db_config: Database configuration
        
    Returns:
        None
    """
    logger.info("Loading data to database")
    
    # Connect to database
    conn = connect_to_database(db_config)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.autocommit = False
        
        # Insert processing log entry
        cursor.execute("""
        INSERT INTO data_processing_log (process_name, status)
        VALUES ('data_loading', 'STARTED')
        """)
        
        # Load customers with upsert strategy
        customers_data = [tuple(row) for row in data_dict['customers'].values]
        customers_query = """
        INSERT INTO customers (customer_id, country, first_purchase_date, 
                              last_purchase_date, total_purchases, total_spent)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (customer_id) DO UPDATE SET
            country = EXCLUDED.country,
            first_purchase_date = EXCLUDED.first_purchase_date,
            last_purchase_date = EXCLUDED.last_purchase_date,
            total_purchases = EXCLUDED.total_purchases,
            total_spent = EXCLUDED.total_spent
        """
        execute_many(cursor, customers_query, customers_data)
        logger.info(f"Inserted {len(customers_data)} customer records")
        
        # Load products with upsert strategy
        products_data = [tuple(row) for row in data_dict['products'].values]
        products_query = """
        INSERT INTO products (product_id, description, unit_price, category, stock_code)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            description = EXCLUDED.description,
            unit_price = EXCLUDED.unit_price,
            category = EXCLUDED.category,
            stock_code = EXCLUDED.stock_code
        """
        execute_many(cursor, products_query, products_data)
        logger.info(f"Inserted {len(products_data)} product records")
        
        # Load orders with upsert strategy to handle duplicates
        orders_data = [tuple(row) for row in data_dict['orders'].values]
        orders_query = """
        INSERT INTO orders (order_id, customer_id, order_date, country, total_amount)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            order_date = EXCLUDED.order_date,
            country = EXCLUDED.country,
            total_amount = EXCLUDED.total_amount
        """
        execute_many(cursor, orders_query, orders_data)
        logger.info(f"Inserted/Updated {len(orders_data)} order records")
        
        # For order_items, we need to delete existing items for the orders we're updating
        # and then insert the new ones to avoid duplicate entries
        order_ids = tuple(data_dict['orders']['order_id'].unique())
        if order_ids:
            # Delete existing order items for these orders
            if len(order_ids) == 1:
                # Handle single order case
                cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_ids[0],))
            else:
                cursor.execute("DELETE FROM order_items WHERE order_id IN %s", (order_ids,))
        
        # Load order_items
        order_items_data = [tuple(row) for row in data_dict['order_items'].values]
        order_items_query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        execute_many(cursor, order_items_query, order_items_data)
        logger.info(f"Inserted {len(order_items_data)} order item records")
        
        # Update data processing log
        cursor.execute("""
        UPDATE data_processing_log
        SET 
            end_time = CURRENT_TIMESTAMP,
            records_processed = %s,
            status = 'COMPLETED'
        WHERE process_name = 'data_loading' AND end_time IS NULL
        """, (len(customers_data) + len(products_data) + len(orders_data) + len(order_items_data),))
        
        # Commit transaction
        conn.commit()
        logger.info("Database load completed successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading data to database: {str(e)}")
        raise
    
    finally:
        cursor.close()
        conn.close()

def process_data(input_dir, output_dir, db_config=None):
    """
    Main function to process the raw data.
    
    Args:
        input_dir: Directory containing the raw data
        output_dir: Directory to save the processed data
        db_config: Database configuration (optional)
        
    Returns:
        Dictionary of paths to the processed data files
    """
    logger.info(f"Processing data from {input_dir}")
    
    # Find the raw data file
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(('.csv', '.xlsx', '.xls')):
            file_path = os.path.join(input_dir, file_name)
            break
    else:
        raise FileNotFoundError(f"No data file found in {input_dir}")
    
    # Load the raw data
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:  # Excel file
        df = pd.read_excel(file_path)
    
    logger.info(f"Loaded raw data from {file_path}: {len(df)} rows")
    logger.info(f"Columns in raw data: {list(df.columns)}")
    
    # Clean the data
    df_clean = clean_online_retail_data(df)
    
    # Extract product categories
    df_with_categories = extract_product_categories(df_clean)
    
    # Transform to relational model
    data_dict = transform_to_relational_model(df_with_categories)
    
    # Save processed data
    file_paths = save_processed_data(data_dict, output_dir)
    
    # Load data to database if config provided
    if db_config:
        load_data_to_database(data_dict, db_config)
    
    logger.info("Data processing completed successfully")
    return file_paths

if __name__ == "__main__":
    # Setup basic logging when run as a script
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_CONFIG
    
    process_data(RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_CONFIG)