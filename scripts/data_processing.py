import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import re
from scripts.db_utils import connect_to_database, execute_many

logger = logging.getLogger(__name__)

def clean_online_retail_data(df):
    logger.info("Starting data cleaning process")
    initial_rows = len(df)

    df_clean = df.copy()

    logger.info(f"Actual columns in dataframe: {list(df_clean.columns)}")

    if 'InvoiceDate' in df_clean.columns:
        df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'], errors='coerce')

    logger.info(f"Missing values before cleaning: {df_clean.isnull().sum().sum()}")

    if 'CustomerID' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['CustomerID'])
        df_clean['CustomerID'] = df_clean['CustomerID'].astype(str)

    if 'InvoiceNo' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['InvoiceNo'])

        df_clean['InvoiceNo'] = df_clean['InvoiceNo'].astype(str)

        if df_clean['InvoiceNo'].str.startswith('C').any():
            df_clean = df_clean[~df_clean['InvoiceNo'].str.startswith('C')]

    if 'Quantity' in df_clean.columns and 'UnitPrice' in df_clean.columns:
        df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]

        df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']

    if 'Description' in df_clean.columns:
        df_clean['Description'].fillna('Unknown', inplace=True)

    if 'UnitPrice' in df_clean.columns and 'Quantity' in df_clean.columns:
        price_mean = df_clean['UnitPrice'].mean()
        price_std = df_clean['UnitPrice'].std()
        quantity_mean = df_clean['Quantity'].mean()
        quantity_std = df_clean['Quantity'].std()
        
        df_clean = df_clean[
            (df_clean['UnitPrice'] < price_mean + 3*price_std) &
            (df_clean['Quantity'] < quantity_mean + 3*quantity_std)
        ]

    final_rows = len(df_clean)
    logger.info(f"Rows before cleaning: {initial_rows}")
    logger.info(f"Rows after cleaning: {final_rows}")
    logger.info(f"Removed {initial_rows - final_rows} rows ({(initial_rows - final_rows) / initial_rows:.2%})")
    logger.info(f"Missing values after cleaning: {df_clean.isnull().sum().sum()}")
    
    return df_clean

def extract_product_categories(df):
    logger.info("Extracting product categories")

    df_with_categories = df.copy()

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

    def determine_category(desc):
        if pd.isna(desc) or desc == 'Unknown':
            return 'Unknown'
        
        desc_lower = str(desc).lower()
        
        for category, pattern in category_patterns.items():
            if re.search(pattern, desc_lower):
                return category
        
        return 'Other'

    if 'Description' in df_with_categories.columns:
        df_with_categories['Category'] = df_with_categories['Description'].apply(determine_category)

        category_counts = df_with_categories['Category'].value_counts()
        logger.info(f"Extracted {len(category_counts)} product categories")
        logger.info(f"Category distribution:\n{category_counts}")
    else:
        logger.warning("Description column not found in dataframe")
        df_with_categories['Category'] = 'Unknown'
    
    return df_with_categories

def transform_to_relational_model(df):
    logger.info("Transforming UCI Online Retail data to relational model")

    customers = df.groupby('CustomerID').agg(
        Country=('Country', 'first'),
        FirstPurchase=('InvoiceDate', 'min'),
        LastPurchase=('InvoiceDate', 'max'),
        TotalPurchases=('InvoiceNo', lambda x: x.nunique()),
        TotalSpent=('TotalPrice', 'sum')
    ).reset_index()

    customers['FirstPurchase'] = pd.to_datetime(customers['FirstPurchase']).dt.date
    customers['LastPurchase'] = pd.to_datetime(customers['LastPurchase']).dt.date

    customers.columns = ['customer_id', 'country', 'first_purchase_date', 
                        'last_purchase_date', 'total_purchases', 'total_spent']

    products = df.drop_duplicates(subset=['StockCode']).copy()
    products['product_id'] = 'P' + products['StockCode'].astype(str)
    products = products[['product_id', 'Description', 'UnitPrice', 'Category', 'StockCode']]
    products.columns = ['product_id', 'description', 'unit_price', 'category', 'stock_code']

    orders = df.groupby(['InvoiceNo', 'CustomerID', 'InvoiceDate', 'Country']).agg(
        TotalAmount=('TotalPrice', 'sum')
    ).reset_index()
    
    orders.columns = ['order_id', 'customer_id', 'order_date', 'country', 'total_amount']

    order_items = df.copy()
    order_items['product_id'] = 'P' + order_items['StockCode'].astype(str)
    order_items = order_items[['InvoiceNo', 'product_id', 'Quantity', 'UnitPrice', 'TotalPrice']]
    order_items.columns = ['order_id', 'product_id', 'quantity', 'unit_price', 'total_price']

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
    logger.info("Loading data to database")

    conn = connect_to_database(db_config)
    cursor = conn.cursor()
    
    try:
        conn.autocommit = False

        cursor.execute("""
        INSERT INTO data_processing_log (process_name, status)
        VALUES ('data_loading', 'STARTED')
        """)

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

        order_ids = tuple(data_dict['orders']['order_id'].unique())
        if order_ids:
            if len(order_ids) == 1:
                cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_ids[0],))
            else:
                cursor.execute("DELETE FROM order_items WHERE order_id IN %s", (order_ids,))

        order_items_data = [tuple(row) for row in data_dict['order_items'].values]
        order_items_query = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        execute_many(cursor, order_items_query, order_items_data)
        logger.info(f"Inserted {len(order_items_data)} order item records")

        cursor.execute("""
        UPDATE data_processing_log
        SET 
            end_time = CURRENT_TIMESTAMP,
            records_processed = %s,
            status = 'COMPLETED'
        WHERE process_name = 'data_loading' AND end_time IS NULL
        """, (len(customers_data) + len(products_data) + len(orders_data) + len(order_items_data),))

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
    logger.info(f"Processing data from {input_dir}")

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(('.csv', '.xlsx', '.xls')):
            file_path = os.path.join(input_dir, file_name)
            break
    else:
        raise FileNotFoundError(f"No data file found in {input_dir}")

    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    logger.info(f"Loaded raw data from {file_path}: {len(df)} rows")
    logger.info(f"Columns in raw data: {list(df.columns)}")

    df_clean = clean_online_retail_data(df)

    df_with_categories = extract_product_categories(df_clean)

    data_dict = transform_to_relational_model(df_with_categories)

    file_paths = save_processed_data(data_dict, output_dir)

    if db_config:
        load_data_to_database(data_dict, db_config)
    
    logger.info("Data processing completed successfully")
    return file_paths

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_CONFIG
    
    process_data(RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_CONFIG)