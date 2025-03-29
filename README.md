# E-commerce Sales & Customer Analysis

A comprehensive data analysis project that analyzes e-commerce sales data using Python, SQL, and Tableau/Power BI visualizations.

## Project Overview

This project provides a complete pipeline for processing and analyzing e-commerce data:

1. **Data Acquisition**: Downloads or generates e-commerce transaction data
2. **Data Storage**: Creates a relational database schema and loads the data
3. **Data Processing**: Cleans, transforms, and prepares the data for analysis
4. **Customer Segmentation**: Performs RFM (Recency, Frequency, Monetary) analysis
5. **Sales Analysis**: Analyzes sales trends, product performance, and geographic distribution
6. **Visualization**: Creates interactive dashboards in Tableau and/or Power BI

## Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL or SQLite
- Tableau or Power BI (for visualization)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ecommerce-analysis.git
   cd ecommerce-analysis
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a PostgreSQL database (optional, SQLite can be used as an alternative):
   ```
   createdb ecommerce_db
   createuser ecommerce_user -P
   ```

5. Update `config.py` with your database settings.

## Usage

### Running the Complete Pipeline

Run the full data pipeline with all steps:

```
python main.py --steps all
```

### Running Specific Steps

Run specific steps of the pipeline:

```
python main.py --steps acquisition database processing rfm sales
```

### Using Sample Data

Generate and use synthetic data instead of downloading:

```
python main.py --steps all --sample
```

### Resetting the Database

If you need to reset the database and start fresh:

```
python reset_database.py
```

## Data Model

The project uses a relational data model with the following tables:

- **customers**: Customer information and summary statistics
- **products**: Product details and categories
- **orders**: Order header information
- **order_items**: Line items for each order
- **customer_segments**: Results of RFM analysis and customer segmentation

## Analysis Features

### Customer Segmentation (RFM Analysis)

- Recency: How recently a customer has made a purchase
- Frequency: How often a customer makes purchases
- Monetary Value: How much a customer spends

Customers are segmented into categories like:
- **Champions** (high value, recent, frequent purchases)
- **Loyal Customers** (consistent shoppers with good recency)
- **Potential Loyalists** (recent shoppers with moderate frequency/spending)
- **New Customers** (recent first purchase)
- **Promising** (recent shoppers with lower frequency/spending)
- **At Risk** (high value, low recency)
- **Need Attention** (moderate value, low recency)
- **About to Sleep** (decreasing activity)
- **Hibernating** (lowest activity, least recent customers)
- **Cannot Lose** (valuable customers with declining activity)

### Sales Analysis

- Time-based trends (daily, monthly, quarterly)
- Product performance analysis
- Geographic sales distribution
- Customer segment performance

### Key Insights Available

- Customer lifetime value by segment
- Product category performance and trends
- Geographic distribution of sales and customer base
- Time-based patterns in purchasing behavior
- Customer acquisition and retention metrics

## Visualization

The project includes instructions for creating interactive dashboards in both:

1. **Tableau**: See `visualization/tableau_instructions.md`
2. **Power BI**: See `visualization/powerbi_instructions.md`

Dashboards include:
- Sales Overview
- Customer Segmentation
- Product Analysis
- Geographic Analysis
- Customer Purchase Behavior

## Project Structure

```
e-commerce-analysis/
├── data/                      # Data directory
│   ├── raw/                   # Raw data files
│   └── processed/             # Processed data files
├── database/                  # Database scripts
│   ├── schema.sql             # Database schema
│   ├── create_tables.sql      # Table creation scripts
│   ├── load_data.sql          # Data import scripts
│   └── analysis_views.sql     # SQL views for analysis
├── notebooks/                 # Jupyter notebooks
│   └── exploratory_analysis.ipynb
├── scripts/                   # Python scripts
│   ├── data_acquisition.py    # Data downloading/generation
│   ├── data_processing.py     # Data cleaning and transformation
│   ├── customer_segmentation.py # RFM analysis
│   ├── sales_analysis.py      # Sales trends analysis
│   └── db_utils.py            # Database utility functions
├── visualization/             # Visualization instructions
│   ├── tableau_instructions.md
│   └── powerbi_instructions.md
├── logs/                      # Pipeline execution logs
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── reset_database.py          # Utility to reset the database
└── main.py                    # Main orchestration script
```

## Performance Considerations

Based on test runs with the UCI Online Retail dataset:
- Processing ~540,000 records takes approximately 1-2 minutes
- Database operations are optimized with proper indexing
- Memory requirements are modest (~500MB RAM)
- Visualization data is pre-aggregated using SQL views for optimal dashboard performance

## Extending the Project

This project can be extended in several ways:

1. **Add Predictive Analytics**: 
   - Implement customer churn prediction models
   - Build sales forecasting using time series analysis
   - Develop product recommendation systems

2. **Integrate with APIs**: 
   - Connect to Shopify, WooCommerce, or other e-commerce platforms
   - Implement real-time data ingestion
   - Add scheduled data refreshes

3. **Enhance Visualizations**: 
   - Create additional specialized dashboards
   - Add interactive what-if analysis features
   - Implement geographic heat maps for regional analysis

4. **Marketing Analysis**:
   - Add support for analyzing marketing campaigns
   - Implement A/B testing analysis
   - Add customer journey mapping

5. **Web Application**: 
   - Develop a web interface using Flask or Django
   - Add user authentication and role-based access
   - Enable custom report generation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- UCI Machine Learning Repository for the Online Retail dataset
- The Pandas, Matplotlib, and Seaborn development teams
- PostgreSQL and SQLite database engines