import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.db_utils import connect_to_database, execute_query, execute_many


logger = logging.getLogger(__name__)

def calculate_rfm_scores(customers_df):
    logger.info("Calculating RFM scores")
    
    rfm_df = customers_df.copy()
    
    if isinstance(rfm_df['last_purchase_date'].iloc[0], str):
        rfm_df['last_purchase_date'] = pd.to_datetime(rfm_df['last_purchase_date'])
    if isinstance(rfm_df['first_purchase_date'].iloc[0], str):
        rfm_df['first_purchase_date'] = pd.to_datetime(rfm_df['first_purchase_date'])
    
    current_date = datetime.now().date()
    rfm_df['recency_days'] = (pd.to_datetime(current_date) - pd.to_datetime(rfm_df['last_purchase_date'])).dt.days
    

    try:
        rfm_df['recency_score'] = pd.qcut(
            rfm_df['recency_days'], 
            q=5,
            labels=[5, 4, 3, 2, 1],
            duplicates='drop'
        )
    except ValueError:
        rfm_df['recency_score'] = pd.cut(
            rfm_df['recency_days'],
            bins=[0, 7, 30, 90, 180, float('inf')],
            labels=[5, 4, 3, 2, 1],
            include_lowest=True
        )
    
    try:
        rfm_df['frequency_score'] = pd.qcut(
            rfm_df['total_purchases'].clip(lower=1),
            q=5,
            labels=[1, 2, 3, 4, 5],
            duplicates='drop'
        )
    except ValueError:
        rfm_df['frequency_score'] = pd.cut(
            rfm_df['total_purchases'].clip(lower=1),
            bins=[0, 1, 2, 5, 10, float('inf')],
            labels=[1, 2, 3, 4, 5],
            include_lowest=True
        )
    
    try:
        rfm_df['monetary_score'] = pd.qcut(
            rfm_df['total_spent'].clip(lower=0.01),
            q=5,
            labels=[1, 2, 3, 4, 5],
            duplicates='drop'
        )
    except ValueError:
        rfm_df['monetary_score'] = pd.cut(
            rfm_df['total_spent'].clip(lower=0.01),
            bins=[0, 10, 50, 100, 500, float('inf')],
            labels=[1, 2, 3, 4, 5],
            include_lowest=True
        )

    for col in ['recency_score', 'frequency_score', 'monetary_score']:
        rfm_df[col] = rfm_df[col].astype(int)
    
    rfm_df['rfm_score'] = rfm_df['recency_score'] + rfm_df['frequency_score'] + rfm_df['monetary_score']
    
    def assign_segment(row):
        r, f, m = row['recency_score'], row['frequency_score'], row['monetary_score']
        rfm = row['rfm_score']
        
        if rfm >= 13:
            return 'Champions'
        elif r >= 4 and (f >= 4 or m >= 4):
            return 'Loyal Customers'
        elif (r >= 3) and (f >= 3 and m >= 3):
            return 'Potential Loyalists'
        elif (r >= 4) and (f <= 2 and m <= 2):
            return 'New Customers'
        elif (r >= 3) and (f <= 2 and m <= 2):
            return 'Promising'
        elif (r <= 2) and (f >= 4 and m >= 4):
            return 'At Risk'
        elif (r <= 2) and (f >= 3 and m >= 3):
            return 'Need Attention'
        elif (r <= 2) and (f <= 2 and m >= 3):
            return 'About to Sleep'
        elif (r <= 2) and (f <= 2 and m <= 2):
            return 'Hibernating'
        else:
            return 'Cannot Lose'
    
    rfm_df['segment'] = rfm_df.apply(assign_segment, axis=1)
    
    segment_counts = rfm_df['segment'].value_counts()
    logger.info(f"Customer segments created:\n{segment_counts}")
    
    return rfm_df[['customer_id', 'recency_score', 'frequency_score', 'monetary_score', 'rfm_score', 'segment']]

def save_rfm_analysis(rfm_df, output_dir):
    logger.info(f"Saving RFM analysis results to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    rfm_path = os.path.join(output_dir, "customer_segments.csv")
    rfm_df.to_csv(rfm_path, index=False)
    logger.info(f"Saved RFM data to {rfm_path}")
    
    plt.figure(figsize=(12, 6))
    segment_counts = rfm_df['segment'].value_counts()
    ax = sns.barplot(x=segment_counts.index, y=segment_counts.values)
    plt.title('Customer Segment Distribution')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Number of Customers')
    plt.tight_layout()

    viz_path = os.path.join(output_dir, "segment_distribution.png")
    plt.savefig(viz_path)
    logger.info(f"Saved segment distribution visualization to {viz_path}")
    
    plt.figure(figsize=(12, 8))
    plt.subplot(3, 1, 1)
    sns.countplot(x='recency_score', data=rfm_df)
    plt.title('Recency Score Distribution')
    
    plt.subplot(3, 1, 2)
    sns.countplot(x='frequency_score', data=rfm_df)
    plt.title('Frequency Score Distribution')
    
    plt.subplot(3, 1, 3)
    sns.countplot(x='monetary_score', data=rfm_df)
    plt.title('Monetary Score Distribution')
    
    plt.tight_layout()
    rfm_viz_path = os.path.join(output_dir, "rfm_score_distribution.png")
    plt.savefig(rfm_viz_path)
    logger.info(f"Saved RFM score distribution visualization to {rfm_viz_path}")
    plt.close()
    return rfm_path

def load_rfm_to_database(rfm_df, db_config):
    logger.info("Loading RFM results to database")
    
    conn = connect_to_database(db_config)
    cursor = conn.cursor()
    
    try:
        conn.autocommit = False
        
        cursor.execute("DELETE FROM customer_segments")
        
        rfm_data = [tuple(row) for row in rfm_df.values]
        
        query = """
        INSERT INTO customer_segments
            (customer_id, recency_score, frequency_score, monetary_score, rfm_score, segment)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (customer_id) DO UPDATE SET
            recency_score = EXCLUDED.recency_score,
            frequency_score = EXCLUDED.frequency_score,
            monetary_score = EXCLUDED.monetary_score,
            rfm_score = EXCLUDED.rfm_score,
            segment = EXCLUDED.segment
        """
        execute_many(cursor, query, rfm_data)
        conn.commit()
        logger.info(f"Loaded {len(rfm_data)} customer segment records to database")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading RFM data to database: {str(e)}")
        raise
    
    finally:
        cursor.close()
        conn.close()

def perform_rfm_analysis(db_config=None, output_dir=None):
    logger.info("Starting RFM analysis")
    
    if db_config:
        conn = connect_to_database(db_config)
        query = """
        SELECT
            customer_id, 
            country, 
            first_purchase_date, 
            last_purchase_date, 
            total_purchases, 
            total_spent 
        FROM customers
        """
        customers_df = execute_query(conn, query)
        conn.close()
    else:
        if output_dir and os.path.exists(os.path.join(output_dir, "customers.csv")):
            customers_df = pd.read_csv(os.path.join(output_dir, "customers.csv"))
        else:
            raise ValueError("Either db_config or valid output_dir with customers.csv must be provided")
    
    rfm_df = calculate_rfm_scores(customers_df)
    
    if output_dir:
        save_rfm_analysis(rfm_df, output_dir)
    
    if db_config:
        load_rfm_to_database(rfm_df, db_config)

    logger.info("RFM analysis completed successfully")
    return rfm_df

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    from config import DB_CONFIG, PROCESSED_DATA_DIR

    perform_rfm_analysis(db_config=DB_CONFIG, output_dir=PROCESSED_DATA_DIR)
