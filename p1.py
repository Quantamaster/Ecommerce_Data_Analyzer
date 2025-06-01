# Modified data_ingestion.py

import pandas as pd
import json
import mysql.connector

from mysql.connector import Error
import os
import requests # New import for making HTTP requests

# --- Configuration ---
# MySQL database connection details
DB_CONFIG = {
    'host': 'localhost',  # Or your MySQL host IP/hostname
    'database': 'ecommerce_data',
    'user': 'root',  # Replace with your MySQL username
    'password': ''  # Replace with your MySQL password
}

# API Endpoint for product data
PRODUCT_API_URL = "http://127.0.0.1:5000/products" # URL of our simulated Flask API

# Path to your orders CSV file
DATA_DIR = 'data'
ORDERS_CSV_PATH = os.path.join(DATA_DIR, 'orders.csv')

# --- Database Connection ---
def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print(f"Successfully connected to MySQL database: {DB_CONFIG['database']}")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# --- Data Loading and Processing (Modified for API) ---
def load_product_data_from_api():
    """
    Fetches product data from the simulated API, processes it,
     and returns a single DataFrame.
    """
    try:
        response = requests.get(PRODUCT_API_URL)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        raw_products_data = response.json()
        print(f"Fetched {len(raw_products_data)} products from API: {PRODUCT_API_URL}")

        all_products_df = pd.DataFrame(raw_products_data)

        # Data Cleaning and Type Conversion
        if not all_products_df.empty:
            # Ensure consistent column names (if API doesn't guarantee it, which ours does now)
            # This step is less critical if your API already provides harmonized data,
            # but good to keep for robustness.
            all_products_df = all_products_df.rename(columns={
                'item_id': 'product_id', # Example of renaming if API has inconsistent fields
                'product_title': 'name',
                'department': 'category',
                'manufacturer': 'brand',
                'cost': 'price',
                'avg_review_score': 'rating',
                'num_reviews': 'reviews_count'
            })

            # Ensure all expected columns are present, fill missing if necessary
            expected_cols = ['product_id', 'name', 'category', 'brand', 'price', 'rating', 'reviews_count']
            for col in expected_cols:
                if col not in all_products_df.columns:
                    all_products_df[col] = None # Add missing columns

            # Select and reorder columns to match your desired schema
            all_products_df = all_products_df[expected_cols]


            all_products_df['price'] = pd.to_numeric(all_products_df['price'], errors='coerce')
            all_products_df['rating'] = pd.to_numeric(all_products_df['rating'], errors='coerce')
            all_products_df['reviews_count'] = pd.to_numeric(all_products_df['reviews_count'], errors='coerce').fillna(0).astype(int)

            # Drop rows where essential product_id or name is missing
            all_products_df.dropna(subset=['product_id', 'name'], inplace=True)
            # Remove duplicates based on product_id
            all_products_df.drop_duplicates(subset=['product_id'], inplace=True)
            print(f"Total unique products after API fetch and cleaning: {len(all_products_df)}")
        else:
            print("No product data fetched from API.")

        return all_products_df

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the API server at {PRODUCT_API_URL}.")
        print("Please ensure 'api_server.py' is running before executing this script.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return pd.DataFrame()


def load_order_data():
    """Loads order data from the CSV file."""
    if os.path.exists(ORDERS_CSV_PATH):
        orders_df = pd.read_csv(ORDERS_CSV_PATH)
        # Convert order_date to datetime objects
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        # Ensure product_id is string for consistent merging
        orders_df['product_id'] = orders_df['product_id'].astype(str)
        print(f"Loaded {len(orders_df)} order items from {ORDERS_CSV_PATH}")
        return orders_df
    else:
        print(f"Error: {ORDERS_CSV_PATH} not found.")
        return pd.DataFrame()

# --- Data Loading into MySQL (remains same) ---
def insert_products_into_db(conn, products_df):
    """Inserts product data into the 'products' table."""
    if products_df.empty:
        print("No product data to insert.")
        return

    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO products (product_id, name, category, brand, price, rating, reviews_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        category = VALUES(category),
        brand = VALUES(brand),
        price = VALUES(price),
        rating = VALUES(rating),
        reviews_count = VALUES(reviews_count);
    """
    try:
        data_to_insert = products_df[['product_id', 'name', 'category', 'brand', 'price', 'rating', 'reviews_count']].values.tolist()
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        print(f"Successfully inserted/updated {cursor.rowcount} products into 'products' table.")
    except Error as e:
        print(f"Error inserting products: {e}")
    finally:
        cursor.close()

def insert_orders_into_db(conn, orders_df, products_df):
    """
    Inserts order and order item data into 'orders' and 'order_items' tables.
    Requires product prices for unit_price_at_order.
    """
    if orders_df.empty:
        print("No order data to insert.")
        return

    cursor = conn.cursor()

    product_prices = products_df.set_index('product_id')['price'].to_dict()

    unique_orders = orders_df[['order_id', 'customer_id', 'order_date']].drop_duplicates()
    order_insert_sql = """
    INSERT IGNORE INTO orders (order_id, customer_id, order_date)
    VALUES (%s, %s, %s);
    """

    order_item_insert_sql = """
    INSERT INTO order_items (order_id, product_id, quantity, unit_price_at_order)
    VALUES (%s, %s, %s, %s);
    """
    try:
        orders_to_insert = unique_orders.values.tolist()
        cursor.executemany(order_insert_sql, orders_to_insert)
        print(f"Successfully inserted/ignored {cursor.rowcount} unique orders into 'orders' table.")

        order_items_to_insert = []
        for index, row in orders_df.iterrows():
            product_id = row['product_id']
            unit_price = product_prices.get(product_id, 0.0) # Default to 0 if product_id not found in API data
            order_items_to_insert.append((
                row['order_id'],
                product_id,
                row['quantity'],
                unit_price
            ))

        cursor.executemany(order_item_insert_sql, order_items_to_insert)
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} order items into 'order_items' table.")
    except Error as e:
        print(f"Error inserting orders/order items: {e}")
        conn.rollback()
    finally:
        cursor.close()


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load and process product data from API
    products_df = load_product_data_from_api()

    # 2. Load order data from CSV
    orders_df = load_order_data()

    # Continue only if product data was successfully fetched
    if not products_df.empty:
        # 3. Establish database connection
        conn = get_db_connection()

        if conn:
            try:
                # 4. Insert products into MySQL
                insert_products_into_db(conn, products_df)

                # 5. Insert orders and order items into MySQL
                insert_orders_into_db(conn, orders_df, products_df)

            finally:
                if conn.is_connected():
                    conn.close()
                    print("MySQL connection closed.")
        else:
            print("Database connection failed. Data ingestion aborted.")
    else:
        print("Product data not available from API. Data ingestion aborted.")