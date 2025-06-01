# app.py

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go

# --- Configuration ---
# MySQL database connection details (must match data_ingestion.py)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ecommerce_data',

    'user': 'root',  # Replace with your MySQL username
    'password': ''  # Replace with your MySQL password
}

# --- Database Connection and Data Loading ---
@st.cache_resource
def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

@st.cache_data(ttl=3600) # Cache data for 1 hour to improve performance
def load_and_process_data():
    """
    Loads raw data from MySQL, merges it, and performs initial aggregations.
    Returns a DataFrame ready for dashboard display.
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame() # Return empty DataFrame if connection fails

    try:
        # Fetch products data
        products_df = pd.read_sql("SELECT * FROM products", conn)
        products_df['product_id'] = products_df['product_id'].astype(str) # Ensure consistent type

        # Fetch order items data
        order_items_df = pd.read_sql("SELECT * FROM order_items", conn)
        order_items_df['product_id'] = order_items_df['product_id'].astype(str) # Ensure consistent type

        # Fetch orders data (for order_date and customer_id)
        orders_df = pd.read_sql("SELECT order_id, customer_id, order_date FROM orders", conn)
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

        # Merge order_items with products to get product details for each item
        merged_df = pd.merge(order_items_df, products_df, on='product_id', how='left')

        # Merge with orders to get order date and customer ID
        merged_df = pd.merge(merged_df, orders_df, on='order_id', how='left')

        # Calculate total revenue for each order item
        merged_df['item_revenue'] = merged_df['quantity'] * merged_df['unit_price_at_order']

        # Ensure numeric types for calculations
        merged_df['quantity'] = pd.to_numeric(merged_df['quantity'], errors='coerce').fillna(0)
        merged_df['price'] = pd.to_numeric(merged_df['price'], errors='coerce').fillna(0)
        merged_df['rating'] = pd.to_numeric(merged_df['rating'], errors='coerce').fillna(0)
        merged_df['reviews_count'] = pd.to_numeric(merged_df['reviews_count'], errors='coerce').fillna(0)
        merged_df['item_revenue'] = pd.to_numeric(merged_df['item_revenue'], errors='coerce').fillna(0)

        # Drop rows where essential data like product_id or order_id is missing after merges
        merged_df.dropna(subset=['product_id', 'order_id', 'order_date', 'item_revenue'], inplace=True)

        return merged_df
    except Error as e:
        st.error(f"Error loading or processing data from MySQL: {e}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

# --- Dashboard Layout and Logic ---
def main():
    st.set_page_config(layout="wide", page_title="E-commerce Data Analyzer")

    st.title(" E-commerce Product Data Aggregator & Analyzer")
    st.markdown("Explore product performance, sales trends, and key metrics.")

    # Load data (cached)
    with st.spinner('Loading and processing data from database...'):
        df = load_and_process_data()

    if df.empty:
        st.warning("No data available to display. Please ensure MySQL is running and `data_ingestion.py` has been executed.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header(" Filters")

    # Category filter
    all_categories = ['All'] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", all_categories)

    # Brand filter
    all_brands = ['All'] + sorted(df['brand'].dropna().unique().tolist())
    selected_brand = st.sidebar.selectbox("Select Brand", all_brands)

    # Date range filter
    min_date = df['order_date'].min().date() if not df['order_date'].empty else pd.to_datetime('2024-01-01').date()
    max_date = df['order_date'].max().date() if not df['order_date'].empty else pd.to_datetime('2024-12-31').date()
    date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))

    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_brand != 'All':
        filtered_df = filtered_df[filtered_df['brand'] == selected_brand]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['order_date'].dt.date >= start_date) &
                                  (filtered_df['order_date'].dt.date <= end_date)]
    elif len(date_range) == 1: # Handle case where only one date is selected (e.g., initial state)
        start_date = date_range[0]
        filtered_df = filtered_df[filtered_df['order_date'].dt.date >= start_date]


    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
        return

    # --- Main Dashboard Content ---
    st.header("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)

    total_revenue = filtered_df['item_revenue'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_products_sold = filtered_df['quantity'].sum()

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Total Products Sold", f"{total_products_sold:,}")

    st.markdown("---")

    # --- Sales Trends Over Time ---
    st.header("Sales Trends Over Time")
    # Aggregate daily revenue
    daily_sales = filtered_df.groupby(pd.Grouper(key='order_date', freq='D'))['item_revenue'].sum().reset_index()
    daily_sales.columns = ['Date', 'Revenue']

    if not daily_sales.empty:
        fig_time_series = px.line(daily_sales, x='Date', y='Revenue',
                                  title='Daily Revenue Trend',
                                  labels={'Revenue': 'Revenue ($)', 'Date': 'Order Date'},
                                  template='plotly_white')
        fig_time_series.update_traces(mode='lines+markers')
        fig_time_series.update_layout(hovermode="x unified")
        st.plotly_chart(fig_time_series, use_container_width=True)
    else:
        st.info("No sales data for the selected period.")

    st.markdown("---")

    # --- Product Performance ---
    st.header("Product Performance")
    col_prod1, col_prod2 = st.columns(2)

    # Top 10 Products by Revenue
    top_products_revenue = filtered_df.groupby('product_id').agg(
        total_revenue=('item_revenue', 'sum'),
        total_quantity=('quantity', 'sum'),
        product_name=('name', 'first'),
        category=('category', 'first'),
        brand=('brand', 'first')
    ).sort_values(by='total_revenue', ascending=False).head(10).reset_index()

    with col_prod1:
        st.subheader("Top 10 Products by Revenue")
        if not top_products_revenue.empty:
            fig_top_revenue = px.bar(top_products_revenue, x='product_name', y='total_revenue',
                                     title='Top Products by Revenue',
                                     labels={'total_revenue': 'Total Revenue ($)', 'product_name': 'Product Name'},
                                     template='plotly_white')
            fig_top_revenue.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top_revenue, use_container_width=True)
        else:
            st.info("No products found for the selected filters.")

    # Sales by Category
    sales_by_category = filtered_df.groupby('category')['item_revenue'].sum().sort_values(ascending=False).reset_index()
    sales_by_category.columns = ['Category', 'Total Revenue']

    with col_prod2:
        st.subheader("Sales by Category")
        if not sales_by_category.empty:
            fig_category_sales = px.pie(sales_by_category, values='Total Revenue', names='Category',
                                        title='Revenue Distribution by Category',
                                        hole=0.3)
            st.plotly_chart(fig_category_sales, use_container_width=True)
        else:
            st.info("No category sales data for the selected filters.")

    st.markdown("---")

    # --- Detailed Product List ---
    st.header("Detailed Product List and Sales Data")
    # Aggregate product details with sales metrics
    product_summary = filtered_df.groupby('product_id').agg(
        Product_Name=('name', 'first'),
        Category=('category', 'first'),
        Brand=('brand', 'first'),
        Price=('price', 'first'),
        Average_Rating=('rating', 'first'),
        Total_Reviews=('reviews_count', 'first'),
        Total_Quantity_Sold=('quantity', 'sum'),
        Total_Revenue=('item_revenue', 'sum'),
        Number_of_Orders=('order_id', 'nunique')
    ).reset_index()

    # Format columns for display
    product_summary['Price'] = product_summary['Price'].map('${:,.2f}'.format)
    product_summary['Total_Revenue'] = product_summary['Total_Revenue'].map('${:,.2f}'.format)
    product_summary['Average_Rating'] = product_summary['Average_Rating'].map('{:.2f}'.format)

    st.dataframe(product_summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("Developed with  using Streamlit, Pandas, and MySQL.")

if __name__ == "__main__":
    main()