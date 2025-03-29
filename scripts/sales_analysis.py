import os
import logging

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.db_utils import connect_to_database, execute_query

logger = logging.getLogger(__name__)
def analyze_time_based_trends(conn):
    logger.info("Analyzing time-based sales trends")

    daily_query = """
    SELECT * FROM vw_daily_sales
    ORDER BY sale_date
    """
    daily_sales = execute_query(conn, daily_query)

    monthly_query = """
    SELECT * FROM vw_monthly_sales
    ORDER BY month
    """
    monthly_sales = execute_query(conn, monthly_query)

    quarterly_query = """
    SELECT 
        DATE_TRUNC('quarter', order_date) AS quarter,
        COUNT(DISTINCT order_id) AS num_orders,
        COUNT(DISTINCT customer_id) AS num_customers,
        SUM(total_amount) AS total_revenue,
        SUM(total_amount) / COUNT(DISTINCT order_id) AS average_order_value
    FROM orders
    GROUP BY quarter
    ORDER BY quarter
    """
    quarterly_sales = execute_query(conn, quarterly_query)

    if len(monthly_sales) > 1:
        monthly_sales['revenue_growth'] = monthly_sales['total_revenue'].pct_change() * 100
        monthly_sales['order_growth'] = monthly_sales['num_orders'].pct_change() * 100
        monthly_sales['customer_growth'] = monthly_sales['num_customers'].pct_change() * 100
    
    return {
        'daily': daily_sales,
        'monthly': monthly_sales,
        'quarterly': quarterly_sales
    }
def analyze_product_performance(conn):
    logger.info("Analyzing product performance")

    top_products_query = """
    SELECT * FROM vw_product_sales
    ORDER BY total_revenue DESC
    LIMIT 20
    """
    top_products = execute_query(conn, top_products_query)

    categories_query = """
    SELECT * FROM vw_category_analysis
    ORDER BY total_revenue DESC
    """
    categories = execute_query(conn, categories_query)
    
    return {
        'top_products': top_products,
        'categories': categories
    }
def analyze_geographic_distribution(conn):
    logger.info("Analyzing geographic distribution")

    country_query = """
    SELECT * FROM vw_country_sales
    ORDER BY total_revenue DESC
    """
    country_sales = execute_query(conn, country_query)
    
    return country_sales
def analyze_customer_segments(conn):
    logger.info("Analyzing customer segment performance")

    segment_query = """
    SELECT * FROM vw_segment_performance
    ORDER BY total_segment_revenue DESC
    """
    segment_performance = execute_query(conn, segment_query)
    
    return segment_performance
def save_analysis_results(analysis_results, output_dir):
    logger.info(f"Saving analysis results to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "visualizations"), exist_ok=True)
    
    file_paths = {}

    if 'time_based' in analysis_results:
        # Monthly sales trend
        if len(analysis_results['time_based']['monthly']) > 1:
            plt.figure(figsize=(12, 6))
            plt.plot(analysis_results['time_based']['monthly']['month'], 
                    analysis_results['time_based']['monthly']['total_revenue'])
            plt.title('Monthly Sales Trend')
            plt.xlabel('Month')
            plt.ylabel('Revenue')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save visualization
            viz_path = os.path.join(output_dir, "visualizations", "monthly_sales_trend.png")
            plt.savefig(viz_path)
            file_paths['monthly_trend_viz'] = viz_path
            plt.close()

        monthly_path = os.path.join(output_dir, "monthly_sales.csv")
        analysis_results['time_based']['monthly'].to_csv(monthly_path, index=False)
        file_paths['monthly_sales'] = monthly_path
    
    # Product analysis
    if 'product' in analysis_results:
        # Top products
        plt.figure(figsize=(12, 8))
        top_10 = analysis_results['product']['top_products'].head(10)
        sns.barplot(x='total_revenue', y='description', data=top_10)
        plt.title('Top 10 Products by Revenue')
        plt.xlabel('Revenue')
        plt.tight_layout()
        
        # Save visualization
        viz_path = os.path.join(output_dir, "visualizations", "top_products.png")
        plt.savefig(viz_path)
        file_paths['top_products_viz'] = viz_path
        plt.close()
        
        # Category performance
        plt.figure(figsize=(12, 6))
        sns.barplot(x='category', y='total_revenue', data=analysis_results['product']['categories'])
        plt.title('Revenue by Product Category')
        plt.xlabel('Category')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save visualization
        viz_path = os.path.join(output_dir, "visualizations", "category_revenue.png")
        plt.savefig(viz_path)
        file_paths['category_viz'] = viz_path
        plt.close()
        
        # Save product data
        products_path = os.path.join(output_dir, "top_products.csv")
        analysis_results['product']['top_products'].to_csv(products_path, index=False)
        file_paths['top_products'] = products_path
        
        categories_path = os.path.join(output_dir, "product_categories.csv")
        analysis_results['product']['categories'].to_csv(categories_path, index=False)
        file_paths['categories'] = categories_path
    
    # Geographic analysis
    if 'geographic' in analysis_results:
        # Country performance
        plt.figure(figsize=(12, 8))
        top_countries = analysis_results['geographic'].head(10)
        sns.barplot(x='total_revenue', y='country', data=top_countries)
        plt.title('Top 10 Countries by Revenue')
        plt.xlabel('Revenue')
        plt.tight_layout()
        
        # Save visualization
        viz_path = os.path.join(output_dir, "visualizations", "country_revenue.png")
        plt.savefig(viz_path)
        file_paths['country_viz'] = viz_path
        plt.close()
        
        # Save geographic data
        geo_path = os.path.join(output_dir, "country_sales.csv")
        analysis_results['geographic'].to_csv(geo_path, index=False)
        file_paths['geographic'] = geo_path
    
    # Customer segment analysis
    if 'segments' in analysis_results:
        # Segment performance
        plt.figure(figsize=(12, 6))
        sns.barplot(x='segment', y='total_segment_revenue', data=analysis_results['segments'])
        plt.title('Revenue by Customer Segment')
        plt.xlabel('Segment')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save visualization
        viz_path = os.path.join(output_dir, "visualizations", "segment_revenue.png")
        plt.savefig(viz_path)
        file_paths['segment_viz'] = viz_path
        plt.close()
        
        # Save segment data
        segments_path = os.path.join(output_dir, "segment_performance.csv")
        analysis_results['segments'].to_csv(segments_path, index=False)
        file_paths['segments'] = segments_path
    
    logger.info(f"Saved analysis results and visualizations to {output_dir}")
    return file_paths

def analyze_sales(db_config, output_dir=None):   
    logger.info("Starting sales analysis")

    conn = connect_to_database(db_config)
    
    try:
        time_based = analyze_time_based_trends(conn)
        product = analyze_product_performance(conn)
        geographic = analyze_geographic_distribution(conn)
        segments = analyze_customer_segments(conn)

        analysis_results = {
            'time_based': time_based,
            'product': product,
            'geographic': geographic,
            'segments': segments
        }

        if output_dir:
            save_analysis_results(analysis_results, output_dir)
        
        logger.info("Sales analysis completed successfully")
        return analysis_results
        
    except Exception as e:
        logger.error(f"Error performing sales analysis: {str(e)}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    from config import DB_CONFIG, PROCESSED_DATA_DIR
    
    analyze_sales(db_config=DB_CONFIG, output_dir=PROCESSED_DATA_DIR)