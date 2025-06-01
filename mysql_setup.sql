-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ecommerce_data;

-- Use the newly created database
USE ecommerce_data;

-- Drop tables if they already exist to ensure a clean slate
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;

-- Create the products table to store a master list of products
-- This table will be populated from the JSON files via the Python script
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2),
    rating DECIMAL(3, 2),
    reviews_count INT
);

-- Create the orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL
);

-- Create the order_items table to link products to orders (many-to-many relationship)
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    -- Store the price at the time of order for accurate historical revenue calculation
    unit_price_at_order DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- You can add indexes for faster query performance, e.g.:
-- CREATE INDEX idx_order_date ON orders(order_date);
-- CREATE INDEX idx_order_items_product_id ON order_items(product_id);
-- CREATE INDEX idx_order_items_order_id ON order_items(order_id);