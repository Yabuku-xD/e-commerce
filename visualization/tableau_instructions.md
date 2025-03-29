# E-commerce Analysis - Tableau Visualization Instructions

This document provides instructions for setting up Tableau dashboards to visualize the e-commerce sales and customer analysis data.

## Database Connection

1. Open Tableau Desktop
2. Select "Connect to Data" > "PostgreSQL" (or your database of choice)
3. Enter the following connection details:
   - Server: localhost (or your database server)
   - Port: 5432 (default PostgreSQL port)
   - Database: ecommerce_db
   - Username: ecommerce_user
   - Password: [your password]
4. Click "Connect"

Alternatively, you can connect to the CSV files directly:
1. Select "Connect to Data" > "Text File"
2. Navigate to the `data/processed` directory
3. Select the CSV files you want to use

## Dashboard 1: Sales Overview Dashboard

### Key Components:

1. **Sales Time Series Chart**
   - Data source: `vw_monthly_sales` view
   - Chart type: Line Chart
   - X-axis: month
   - Y-axis: total_revenue
   - Add month-over-month growth as a secondary line

2. **Sales by Country Map**
   - Data source: `vw_country_sales` view
   - Chart type: Map
   - Location: country
   - Color: total_revenue
   - Size: num_customers

3. **Top Products Bar Chart**
   - Data source: `vw_product_sales` view
   - Chart type: Horizontal Bar Chart
   - Y-axis: description (limit to top 10)
   - X-axis: total_revenue
   - Color: category

4. **Category Performance**
   - Data source: `vw_category_analysis` view
   - Chart type: Pie Chart or Treemap
   - Size: total_revenue
   - Color: category
   - Label: category + percentage of total

5. **KPI Cards**
   - Total Revenue
   - Total Orders
   - Average Order Value
   - Active Customers

### Dashboard Setup:

1. Create individual worksheets for each of the above components
2. Create a new dashboard and add the worksheets
3. Add title: "E-commerce Sales Overview"
4. Add date range filters to filter all visualizations
5. Add category filters to filter product-related visualizations

## Dashboard 2: Customer Segmentation Dashboard

### Key Components:

1. **RFM Segment Distribution**
   - Data source: `vw_segment_performance` view
   - Chart type: Horizontal Bar Chart
   - Y-axis: segment
   - X-axis: num_customers
   - Color: segment

2. **Segment Performance Comparison**
   - Data source: `vw_segment_performance` view
   - Chart type: Bubble Chart
   - X-axis: avg_purchase_frequency
   - Y-axis: avg_customer_spend
   - Size: num_customers
   - Color: segment

3. **Segment Revenue Contribution**
   - Data source: `vw_segment_performance` view
   - Chart type: Pie Chart
   - Size: total_segment_revenue
   - Color: segment
   - Label: segment + percentage of total

4. **Customer Purchase Recency**
   - Data source: `vw_rfm_analysis` view
   - Chart type: Histogram
   - X-axis: recency_days
   - Color: segment

5. **Segment Details Table**
   - Data source: `vw_segment_performance` view
   - Show all metrics for each segment

### Dashboard Setup:

1. Create individual worksheets for each of the above components
2. Create a new dashboard and add the worksheets
3. Add title: "Customer Segmentation Analysis"
4. Add segment filters to filter all visualizations
5. Add country filters to see segment distribution by country

## Dashboard 3: Product Analysis Dashboard

### Key Components:

1. **Product Performance Over Time**
   - Data source: Join of `orders`, `order_items`, and `products` tables
   - Chart type: Line Chart
   - X-axis: month (from order_date)
   - Y-axis: sum of total_price
   - Color: top 5 products or categories

2. **Product Category Breakdown**
   - Data source: `vw_category_analysis` view
   - Chart type: Stacked Bar Chart
   - X-axis: category
   - Y-axis: total_revenue
   - Color: num_products

3. **Product Performance Quadrant**
   - Data source: `vw_product_sales` view
   - Chart type: Scatter Plot
   - X-axis: num_orders
   - Y-axis: total_revenue
   - Size: total_quantity_sold
   - Color: category

4. **Best Sellers by Country**
   - Data source: Join of `orders`, `order_items`, and `products` tables
   - Chart type: Heat Map
   - Rows: top 10 products
   - Columns: top 10 countries
   - Color: total_price sum

### Dashboard Setup:

1. Create individual worksheets for each of the above components
2. Create a new dashboard and add the worksheets
3. Add title: "Product Performance Analysis"
4. Add date range filters to filter all visualizations
5. Add category filters for product filtering

## Dashboard 4: Customer Purchase Behavior Dashboard

### Key Components:

1. **Customer Purchase Frequency**
   - Data source: `customers` table
   - Chart type: Histogram
   - X-axis: total_purchases
   - Color: grouped by purchase frequency bands

2. **Customer Spending Distribution**
   - Data source: `customers` table
   - Chart type: Histogram
   - X-axis: total_spent
   - Color: grouped by spending bands

3. **Customer Lifecycle**
   - Data source: `customers` table
   - Chart type: Scatter Plot
   - X-axis: first_purchase_date
   - Y-axis: last_purchase_date
   - Color: total_spent
   - Size: total_purchases

4. **Customer Acquisition by Month**
   - Data source: `customers` table
   - Chart type: Line Chart
   - X-axis: month (from first_purchase_date)
   - Y-axis: count of customers
   - Color: country

### Dashboard Setup:

1. Create individual worksheets for each of the above components
2. Create a new dashboard and add the worksheets
3. Add title: "Customer Purchase Behavior"
4. Add country filters for geographic filtering
5. Add date range filters to filter all visualizations

## Customizing Your Dashboards

- **Colors**: Use a consistent color scheme across all dashboards
- **Interactivity**: Add actions to filter between dashboards
- **Tooltips**: Customize tooltips to show additional information on hover
- **Parameters**: Add parameters to allow user-defined thresholds or date ranges
- **Calculated Fields**: Create calculated fields for advanced metrics

## Publishing Your Dashboard

1. Go to Server > Publish Workbook
2. Sign in to your Tableau Server or Tableau Online account
3. Select the project to publish to
4. Configure authentication for the data source
5. Set permissions for who can access the dashboard
6. Click "Publish"

## Tableau Best Practices

1. **Keep it simple**: Focus on the most important insights
2. **Be consistent**: Use consistent formatting, colors, and terminology
3. **Design for your audience**: Consider who will use the dashboard and what decisions they need to make
4. **Provide context**: Add titles, descriptions, and annotations to help users understand the data
5. **Test with users**: Get feedback from potential users to improve the dashboard