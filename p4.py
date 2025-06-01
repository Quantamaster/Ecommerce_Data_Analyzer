# api_server.py
from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# --- Load Product Data (from original JSONs for simplicity) ---
# We'll load the data from your existing JSON files into memory
# to simulate a database or external product catalog for the API.
DATA_DIR = 'data'
PRODUCTS_SOURCE_1_PATH = os.path.join(DATA_DIR, 'products_source_1.json')
PRODUCTS_SOURCE_2_PATH = os.path.join(DATA_DIR, 'products_source_2.json')

all_products_data = []

if os.path.exists(PRODUCTS_SOURCE_1_PATH):
    with open(PRODUCTS_SOURCE_1_PATH, 'r') as f:
        data1 = json.load(f)
    all_products_data.extend(data1)
    print(f"API Server: Loaded {len(data1)} products from {PRODUCTS_SOURCE_1_PATH}")

if os.path.exists(PRODUCTS_SOURCE_2_PATH):
    with open(PRODUCTS_SOURCE_2_PATH, 'r') as f:
        data2 = json.load(f)
    # Simulate schema harmonization on the API side if needed, or handle in client
    # For this simple API, we'll assume the API provides a consistent format eventually.
    # Here, we'll do a basic mapping for source 2 items
    harmonized_data2 = []
    for item in data2:
        harmonized_data2.append({
            "product_id": item.get("item_id"),
            "name": item.get("product_title"),
            "category": item.get("department"),
            "brand": item.get("manufacturer"),
            "price": item.get("cost"),
            "rating": item.get("avg_review_score"),
            "reviews_count": item.get("num_reviews")
        })
    all_products_data.extend(harmonized_data2)
    print(f"API Server: Loaded {len(harmonized_data2)} products from {PRODUCTS_SOURCE_2_PATH} (harmonized)")

print(f"API Server: Total products available: {len(all_products_data)}")

# --- API Endpoints ---
@app.route('/products', methods=['GET'])
def get_products():
    """Returns all product data."""
    return jsonify(all_products_data)

@app.route('/products/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Returns a single product by ID."""
    product = next((p for p in all_products_data if p.get('product_id') == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"message": "Product not found"}), 404

if __name__ == '__main__':
    # It's important to run this server first!
    print("Starting Flask API server on http://127.0.0.1:5000/")
    print("Press Ctrl+C to stop.")
    app.run(debug=True, port=5000)