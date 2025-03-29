# E-commerce Analysis - Power BI Visualization Instructions

This document provides instructions for setting up Power BI dashboards to visualize the e-commerce sales and customer analysis data.

## Database Connection

1. Open Power BI Desktop
2. Click "Get Data" > "Database" > "PostgreSQL database" (or your database of choice)
3. Enter the following connection details:
   - Server: localhost (or your database server)
   - Database: ecommerce_db
   - Data Connectivity mode: Import
4. Click "OK"
5. Enter your database credentials when prompted
6. Select the tables and views you want to import:
   - All views (vw_*)
   - Raw tables if needed (customers, products, orders, order_items)

Alternatively, you can connect to the CSV files directly:
1. Click "Get Data" > "Text/CSV"
2. Navigate to the `data/processed` directory
3. Select the CSV files you want to use

## Data Model Setup

1. **Create Relationships:**
   - Link `orders` to `customers` via `customer_id`
   - Link `orders` to `order_items` via `order_id`
   - Link `order_items` to `products` via `product_id`
   - Link `customers` to `customer_segments` via `customer_id`

2. **Create Date Table:**
   - Create a date dimension table using DAX:
   ```
   Date = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))
   ```
   - Add columns for Year, Quarter, Month, Month Name, Day, etc.
   - Connect to `orders` table via `order_date`

3. **Create Key Measures:**
   ```
   Total Revenue = SUM(orders[total_amount])
   Total Orders = COUNTROWS(orders)
   Average Order Value = DIVIDE([Total Revenue], [Total Orders])
   Total Customers = DISTINCTCOUNT(customers[customer_id])
   ```

## Dashboard 1: Sales Overview Dashboard

### Key Components:

1. **Sales Overview Card:**
   - Create a multi-row card visual with:
     - Total Revenue
     - Total Orders
     - Average Order Value
     - Total Customers

2. **Sales Trend Chart:**
   - Visual: Line chart
   - Axis: Date[Month]
   - Values: Total Revenue, Total Orders
   - Create a combo chart to show both metrics

3. **Sales by Country:**
   - Visual: Map
   - Location: Country
   - Values: Total Revenue, Total Customers
   - Format with data-based color gradients

4. **Top Products:**
   - Visual: Bar chart
   - Axis: products[description] (top 10)
   - Values: Sum of order_items[total_price]
   - Group by products[category]

5. **Category Performance:**
   - Visual: Pie/Donut chart
   - Legend: products[category]
   - Values: Sum of order_items[total_price]

6. **Daily Sales Pattern:**
   - Visual: Heat map (use Matrix visual)
   - Rows: Day of Week
   - Columns: Hour of Day
   - Values: Count of orders

### Dashboard Setup:

1. Create a new page named "Sales Overview"
2. Add the above visuals in a logical layout
3. Add slicers for:
   - Date range
   - Product category
   - Country

## Dashboard 2: Customer Segmentation Dashboard

### Key Components:

1. **Segment Distribution:**
   - Visual: Donut chart
   - Legend: customer_segments[segment]
   - Values: Count of customers

2. **Segment Performance Metrics:**
   - Visual: Card visuals or Gauge charts
   - Create measures for each segment:
   ```
   Champions Count = CALCULATE(COUNTROWS(customer_segments), customer_segments[segment] = "Champions")
   Champions Revenue = CALCULATE(SUM(customers[total_spent]), customer_segments[segment] = "Champions")
   ```

3. **RFM Score Distribution:**
   - Visual: Clustered column chart
   - Axis: [RFM Score bins]
   - Values: Count of customers
   - Create 5 bins for R, F, and M scores

4. **Segment Performance Comparison:**
   - Visual: Scatter chart
   - X-axis: Avg purchase frequency (by segment)
   - Y-axis: Avg monetary value (by segment)
   - Size: Customer count by segment
   - Legend: Segment

5. **Recency Analysis:**
   - Visual: Histogram
   - Axis: [Days since last purchase bins]
   - Values: Count of customers
   - Color: Segment

### Dashboard Setup:

1. Create a new page named "Customer Segmentation"
2. Add the above visuals in a logical layout
3. Add slicers for:
   - Segment
   - Country
   - RFM score range

## Dashboard 3: Product Analysis Dashboard

### Key Components:

1. **Product Performance Table:**
   - Visual: Table
   - Rows: Top 20 products
   - Values:
     - Total Revenue
     - Total Quantity
     - Order Count
     - Average Price
   - Add conditional formatting for easier analysis

2. **Product Performance Over Time:**
   - Visual: Line chart
   - Axis: Date[Month]
   - Values: Sum of total_price
   - Legend: Top 5 products or categories (use TOP N filtering)

3. **Product Category Analysis:**
   - Visual: Column chart
   - Axis: Category
   - Values: Revenue, Product Count (dual axis)

4. **Product Quadrant Analysis:**
   - Visual: Scatter chart
   - X-axis: Order frequency
   - Y-axis: Revenue
   - Create quadrant reference lines using average values
   - Add custom tooltips with product details

5. **Product-Customer Affinity:**
   - Visual: Heat map
   - Rows: Top product categories
   - Columns: Customer segments
   - Values: Sum of total_price or order count

### Dashboard Setup:

1. Create a new page named "Product Analysis"
2. Add the above visuals in a logical layout
3. Add slicers for:
   - Date range
   - Product category
   - Customer segment

## Dashboard 4: Geographic Sales Analysis

### Key Components:

1. **Sales Map:**
   - Visual: Map
   - Location: Country
   - Size: Total Revenue
   - Color: Customer Count or AOV

2. **Country Performance Table:**
   - Visual: Table
   - Rows: Country
   - Values:
     - Revenue
     - Orders
   - Customer Count
     - Average Order Value
     - % of Total Revenue
   - Add conditional formatting for easier analysis

3. **Top Countries Bar Chart:**
   - Visual: Bar chart
   - Axis: Top 10 countries by revenue
   - Values: Total Revenue
   - Add data labels

4. **Country Customer Segments:**
   - Visual: 100% Stacked column chart
   - Axis: Top 10 countries
   - Values: Customer count
   - Legend: Customer segments
   - Show percentage distribution of segments by country

5. **Regional Sales Trend:**
   - Visual: Line chart
   - Axis: Date[Month]
   - Values: Sum of revenue
   - Legend: Top 5 countries
   - Add trend lines

### Dashboard Setup:

1. Create a new page named "Geographic Analysis"
2. Add the above visuals in a logical layout
3. Add slicers for:
   - Date range
   - Customer segment
   - Product category

## Dashboard 5: Customer Purchase Behavior Dashboard

### Key Components:

1. **Customer Lifecycle:**
   - Visual: Scatter chart
   - X-axis: first_purchase_date
   - Y-axis: last_purchase_date
   - Size: total_spent
   - Color: total_purchases or segment

2. **Customer Purchase Frequency:**
   - Visual: Histogram
   - Axis: total_purchases (binned)
   - Values: Count of customers

3. **Customer Spend Distribution:**
   - Visual: Histogram
   - Axis: total_spent (binned)
   - Values: Count of customers

4. **New vs Returning Customers:**
   - Visual: Area chart
   - Axis: Date[Month]
   - Values: Count of new customers, count of returning customers
   - Create measures to identify new customers each month

5. **Customer Retention Rate:**
   - Visual: Line chart
   - Axis: Date[Month]
   - Values: Retention rate
   - Create a measure for retention rate calculation:
   ```
   Retention Rate = 
   DIVIDE(
       CALCULATE(
           DISTINCTCOUNT(orders[customer_id]),
           FILTER(
               ALL(orders),
               orders[customer_id] IN CALCULATETABLE(
                   VALUES(orders[customer_id]),
                   DATEADD(orders[order_date], -1, MONTH)
               )
           )
       ),
       CALCULATE(
           DISTINCTCOUNT(orders[customer_id]),
           DATEADD(orders[order_date], -1, MONTH)
       )
   )
   ```

### Dashboard Setup:

1. Create a new page named "Customer Behavior"
2. Add the above visuals in a logical layout
3. Add slicers for:
   - Date range
   - Customer segment
   - Country

## Custom Theme and Dashboard Styling

1. **Create a Custom Theme:**
   - Go to View > Themes > Customize Current Theme
   - Set branded colors for your visuals
   - Configure font styles and sizes
   - Set default visual properties

2. **Dashboard Layout Best Practices:**
   - Use a consistent grid layout
   - Place high-level KPIs at the top
   - Group related visuals together
   - Include a title and brief description for each page
   - Add your organization's logo

3. **Dynamic Titles and Subtitles:**
   - Use measures in titles to reflect current filter context:
   ```
   Dynamic Title = 
   "Sales Analysis for " & 
   IF(
       ISFILTERED(Date[Year]),
       VALUES(Date[Year]),
       "All Years"
   )
   ```

4. **Add Navigation Buttons:**
   - Create buttons to navigate between dashboard pages
   - Add a home button on each page
   - Consider adding bookmark buttons for pre-filtered views

## Publishing and Sharing

1. **Publish to Power BI Service:**
   - Click "Publish" in Power BI Desktop
   - Select a workspace to publish to
   - Configure scheduled refresh for the dataset

2. **Create a Dashboard in Power BI Service:**
   - Pin the most important visuals from your reports to a dashboard
   - Configure real-time data alerts if needed

3. **Sharing Options:**
   - Share the dashboard with colleagues
   - Configure row-level security if needed
   - Export to PowerPoint or PDF for presentations
   - Embed in SharePoint or other web applications

4. **Mobile View:**
   - Configure phone layout for each report page
   - Test the dashboard on mobile devices

## Power BI Best Practices

1. **Performance Optimization:**
   - Limit the number of visuals per page (5-7 maximum)
   - Use calculated columns sparingly; prefer measures
   - Consider using aggregations for large datasets
   - Review query performance with Performance Analyzer

2. **Design for Your Audience:**
   - Understand who will use the dashboard and what decisions they need to make
   - Arrange visuals in a logical flow that tells a story
   - Include context and insights, not just data

3. **Interactivity:**
   - Configure cross-filtering between visuals
   - Add drill-through pages for detailed analysis
   - Use bookmarks for different analytical views

4. **Documentation:**
   - Document your data model and measures
   - Add tooltips and descriptions to help users understand the data
   - Create a user guide for complex dashboards

## Resources

- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [DAX Guide](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)