#  E-commerce Product Data Aggregator & Analyzer

This project builds a simple yet functional E-commerce data pipeline, from raw product data ingestion and API serving to a comprehensive analytics dashboard. It demonstrates how to integrate Python applications (Flask API, data processing scripts, Streamlit dashboard) with a MySQL database.

---

##  Features

* **Product Data Ingestion:** Fetches product data from multiple JSON sources, harmonizes it, and loads it into a MySQL database.
* **Order Data Ingestion:** Processes order data from a CSV file and inserts it into the MySQL database, maintaining relationships with products.
* **Product Data API:** A Flask-based REST API that serves product data, mimicking an external data source.
* **Interactive Dashboard:** A Streamlit web application for visualizing and analyzing key e-commerce metrics, product performance, and sales trends.
* **MySQL Database:** Stores all product and order information, acting as the central data repository.

---

##  Technologies Used

* **Python 3.x:** Core programming language.
* **Flask:** For building the REST API server.
* **Streamlit:** For creating the interactive web dashboard.
* **Pandas:** For data manipulation and cleaning.
* **Requests:** For making HTTP requests to the API.
* **`mysql-connector-python` or `PyMySQL`:** For connecting Python to MySQL.
* **MySQL / MariaDB:** The relational database (typically via XAMPP).
* **XAMPP:** Provides Apache, MySQL (MariaDB), and PHPMyAdmin for easy local server management.

---

##  Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* **Python 3.8+:** Download from [python.org](https://www.python.org/downloads/).
* **XAMPP:** Download from [apachefriends.org](https://www.apachefriends.org/index.html). Install it to manage your MySQL database and phpMyAdmin.

### 1. Project Setup

1.  **Clone the Repository (or Download):**
    ```bash
    git clone <your-repository-url>
    cd Ecommerce # Or navigate to your project directory if downloaded
    ```

2.  **Create a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    ```

3.  **Activate the Virtual Environment:**
    * **Windows:**
        ```bash
        .\.venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source ./.venv/bin/activate
        ```
    (You should see `(.venv)` at the beginning of your terminal prompt.)

4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (If you don't have `requirements.txt`, you'll need to install them manually: `pip install flask streamlit pandas requests mysql-connector-python`)

### 2. MySQL Database Setup

1.  **Start XAMPP Control Panel:**
    * Start the **Apache** module.
    * Start the **MySQL** module. (Ensure it says "Running" and the light is green. If you face port conflicts, you might need to change MySQL's port in `my.ini` to `3307` as discussed in previous troubleshooting. If you change it, remember this port for your Python `DB_CONFIG`.)

2.  **Access phpMyAdmin:**
    * Open your web browser and go to `http://localhost/phpmyadmin/`.

3.  **Create the Database and Tables:**
    * In phpMyAdmin, go to the **SQL tab**.
    * Open your `mysql_setup.sql` file (located in your project root) in a text editor.
    * **Copy the entire content** of `mysql_setup.sql`.
    * **Paste it into the SQL query box** in phpMyAdmin.
    * Click the **"Go"** button.
    * This will create the `ecommerce_data` database and the `products`, `orders`, and `order_items` tables within it.
    * **Important:** If you faced "Access denied" errors for `root@localhost` earlier, ensure the `root` user is unlocked (typically by setting an empty password or a known password via `ALTER USER` or `UPDATE mysql.user` from the command line after stopping MySQL and restarting with `--skip-grant-tables`).

### 3. Configure Database Connection in Python Scripts

All your Python scripts (`api_server.py`, `data_ingestion.py`, `app.py`) need to know how to connect to your MySQL database.

1.  **Open `api_server.py`, `data_ingestion.py`, and `app.py` in PyCharm.**
2.  **Locate the `DB_CONFIG` dictionary in EACH of these three files.**
3.  **Update `DB_CONFIG`** with your MySQL credentials:
    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'ecommerce_data',
        'user': 'root', # Use 'root' as the username
        'password': '', # If root has no password (common XAMPP default), leave this as an empty string ''
                        # Otherwise, put your root password here.
        'port': 3306    # IMPORTANT: Change to 3307 if you changed MySQL's port in XAMPP!
    }
    ```
4.  **Save all three Python files** after making changes.

### 4. Prepare Product and Order Data

Your project uses `products_source_1.json`, `products_source_2.json`, and `orders.csv` from the `data/` folder.

* **Ensure `products_source_1.json` and `products_source_2.json` collectively contain all `product_id`s that are referenced in `orders.csv`.** If `orders.csv` mentions a product ID (e.g., `P006`) that is not defined in your JSON product sources, you will get a foreign key error during data ingestion.
    * If you encounter a foreign key error, manually add the missing product definitions to one of your `products_source_X.json` files. For example, if `orders.csv` mentions `P006`, ensure `P006` is defined in one of the JSON files.

---
### Overview
![performance chart overview](https://github.com/Quantamaster/Ecommerce_Data_Analyzer/blob/main/performance%20overview%20chart.png)

## ▶ Running the Project Components

You need to run these components in separate terminal tabs in PyCharm, in a specific order:

### 1. Start the Product Data API Server (`api_server.py`)

This server provides the product data that your `data_ingestion.py` script will fetch.

1.  **Open PyCharm's Terminal** (usually at the bottom).
2.  Ensure your virtual environment is active.
3.  Run the Flask API server:
    ```bash
    python api_server.py
    ```
    (You should see output indicating it's running on `http://127.0.0.1:5000/`)
4.  **Leave this terminal tab open and running.**

### 2. Run the Data Ingestion Script (`data_ingestion.py`)

This script populates your MySQL database with products and orders.

1.  **Open a NEW Terminal tab in PyCharm** (do NOT close the `api_server.py` tab).
2.  Ensure your virtual environment is active.
3.  Run the data ingestion script:
    ```bash
    python data_ingestion.py
    ```
4.  Wait for the script to complete (it will return to the prompt). You should see messages indicating successful insertions. If you face errors, check your `DB_CONFIG` or if you've correctly resolved the foreign key constraint by adding missing product definitions.

### 3. Launch the E-commerce Dashboard (`app.py`)

This is your interactive "website"!

1.  **Open a NEW Terminal tab in PyCharm** (do NOT close the `api_server.py` tab).
2.  Ensure your virtual environment is active.
3.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
4.  Your default web browser should automatically open to `http://localhost:8501` (or a similar address displayed in the terminal).

---
### Dashboard

![Dashboard](https://github.com/Quantamaster/Ecommerce_Data_Analyzer/blob/main/Dashboard.png)

##  Exploring the Dashboard

Once the Streamlit app is running in your browser, you can:

* View aggregated product data.
* Analyze sales trends over time.
* Explore product categories and brands.
* Gain insights into your e-commerce operations.

---

## Stopping the Applications

To stop the project components:

* Go to the terminal tabs where `api_server.py` and `app.py` are running.
* Press `Ctrl+C` in each terminal to stop the respective servers.
* You can then close the XAMPP Control Panel.

---


Enjoy exploring your E-commerce Product Data Aggregator & Analyzer!


