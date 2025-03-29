"""
Data Acquisition Module

This module handles the acquisition of e-commerce data either by:
1. Downloading a real dataset from a provided URL
2. Generating synthetic data for testing purposes
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from faker import Faker
import random

# Set up logger for this module
logger = logging.getLogger(__name__)

def download_dataset(url, output_path):
    """
    Download dataset from the provided URL and save it to the output path.
    
    Args:
        url: URL to download the dataset from
        output_path: Path where the downloaded file will be saved
        
    Returns:
        Path to the downloaded file
    """
    logger.info(f"Downloading dataset from {url}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Dataset downloaded successfully to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise

def generate_synthetic_data(output_dir, num_records=10000, start_date="2022-01-01", 
                           end_date="2023-12-31", num_customers=500, 
                           num_products=100, num_countries=15):
    """
    Generate synthetic e-commerce data for testing purposes.
    
    Args:
        output_dir: Directory to save the generated data
        num_records: Number of records (order items) to generate
        start_date: Start date for data generation (YYYY-MM-DD)
        end_date: End date for data generation (YYYY-MM-DD)
        num_customers: Number of unique customers to generate
        num_products: Number of unique products to generate
        num_countries: Number of unique countries to include
        
    Returns:
        Dictionary of paths to the generated files
    """
    logger.info(f"Generating synthetic data with {num_records} records")
    
    fake = Faker()
    
    # Convert dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Generate product data
    product_categories = [
        "Home Decor", "Kitchen", "Garden", "Electronics", "Clothing", 
        "Toys", "Office Supplies", "Jewelry", "Art", "Books"
    ]
    
    products = []
    for i in range(num_products):
        category = random.choice(product_categories)
        products.append({
            'product_id': f"P{i+1:05d}",
            'description': fake.catch_phrase(),
            'unit_price': round(random.uniform(5.0, 200.0), 2),
            'category': category,
            'stock_code': f"SKU{i+1:05d}"
        })
    
    products_df = pd.DataFrame(products)
    
    # Generate customer data
    countries = [fake.country() for _ in range(num_countries)]
    
    customers = []
    for i in range(num_customers):
        customers.append({
            'customer_id': f"C{i+1:05d}",
            'country': random.choice(countries)
        })
    
    customers_df = pd.DataFrame(customers)
    
    # Generate orders and order items
    orders = []
    order_items = []
    order_counter = 0
    
    for i in range(num_records):
        # Randomly determine if this is a new order or adding to existing
        if i == 0 or random.random() < 0.25:  # 25% chance of new order
            order_counter += 1
            order_id = f"O{order_counter:07d}"
            customer = random.choice(customers)
            order_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
            
            orders.append({
                'order_id': order_id,
                'customer_id': customer['customer_id'],
                'order_date': order_date,
                'country': customer['country'],
                'total_amount': 0  # Will update later
            })
        
        # Add an item to the current order
        product = random.choice(products)
        quantity = random.randint(1, 10)
        total_price = round(quantity * product['unit_price'], 2)
        
        order_items.append({
            'order_id': order_id,
            'product_id': product['product_id'],
            'quantity': quantity,
            'unit_price': product['unit_price'],
            'total_price': total_price
        })
        
        # Update order total
        orders[-1]['total_amount'] += total_price
    
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    
    # Update customer data with purchase info
    customer_purchases = orders_df.groupby('customer_id').agg(
        first_purchase_date=('order_date', 'min'),
        last_purchase_date=('order_date', 'max'),
        total_purchases=('order_id', 'nunique'),
        total_spent=('total_amount', 'sum')
    ).reset_index()
    
    customers_df = pd.merge(customers_df, customer_purchases, on='customer_id', how='left')
    
    # Fixed: Properly fill NA values column by column
    customers_df['first_purchase_date'] = customers_df['first_purchase_date'].fillna(pd.NaT)
    customers_df['last_purchase_date'] = customers_df['last_purchase_date'].fillna(pd.NaT)
    customers_df['total_purchases'] = customers_df['total_purchases'].fillna(0)
    customers_df['total_spent'] = customers_df['total_spent'].fillna(0.0)
    
    # Save data to CSV files
    os.makedirs(output_dir, exist_ok=True)
    
    file_paths = {}
    
    # Save products
    product_path = os.path.join(output_dir, "products.csv")
    products_df.to_csv(product_path, index=False)
    file_paths['products'] = product_path
    
    # Save customers
    customer_path = os.path.join(output_dir, "customers.csv")
    customers_df.to_csv(customer_path, index=False)
    file_paths['customers'] = customer_path
    
    # Save orders
    orders_path = os.path.join(output_dir, "orders.csv")
    orders_df.to_csv(orders_path, index=False)
    file_paths['orders'] = orders_path
    
    # Save order items
    order_items_path = os.path.join(output_dir, "order_items.csv")
    order_items_df.to_csv(order_items_path, index=False)
    file_paths['order_items'] = order_items_path
    
    # Save combined raw data (similar format to Online Retail dataset)
    combined_data = []
    
    for _, order in orders_df.iterrows():
        items = order_items_df[order_items_df['order_id'] == order['order_id']]
        for _, item in items.iterrows():
            product = products_df[products_df['product_id'] == item['product_id']].iloc[0]
            combined_data.append({
                'InvoiceNo': order['order_id'],
                'StockCode': product['stock_code'],
                'Description': product['description'],
                'Quantity': item['quantity'],
                'InvoiceDate': order['order_date'],
                'UnitPrice': item['unit_price'],
                'CustomerID': order['customer_id'],
                'Country': order['country']
            })
    
    combined_df = pd.DataFrame(combined_data)
    combined_path = os.path.join(output_dir, "online_retail_synthetic.csv")
    combined_df.to_csv(combined_path, index=False)
    file_paths['combined'] = combined_path
    
    logger.info(f"Generated {len(combined_df)} records across {len(orders_df)} orders")
    logger.info(f"Files saved to {output_dir}")
    
    return file_paths

def acquire_data(output_dir, dataset_url=None):
    """
    Main function to acquire data by downloading from the provided URL.
    
    Args:
        output_dir: Directory to save the data
        dataset_url: URL to download the dataset from
        
    Returns:
        Path to the acquired data file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if not dataset_url:
        raise ValueError("Dataset URL must be provided")
    
    file_ext = dataset_url.split('.')[-1].lower()
    output_path = os.path.join(output_dir, f"online_retail.{file_ext}")
    
    return download_dataset(dataset_url, output_path)

if __name__ == "__main__":
    # Setup basic logging when run as a script
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    from config import RAW_DATA_DIR, DATASET_URL
    acquire_data(RAW_DATA_DIR, use_sample=False, dataset_url=DATASET_URL)