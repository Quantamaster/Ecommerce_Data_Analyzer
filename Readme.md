

---

## 🛒 E-commerce Product Data Aggregator & Analyzer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-API-lightgrey)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue)
![Data%20Pipeline](https://img.shields.io/badge/Data-Pipeline-green)

---
## 📚 Table of Contents

- [Overview](#-overview)
- [Key Capabilities](#-key-capabilities)
- [System Architecture](#-system-architecture)
- [Technologies Used](#-technologies-used)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Database Setup](#-mysql-database-setup)
- [Database Configuration](#-database-configuration)
- [Data Integrity Requirements](#-data-integrity-requirement)
- [Running the Pipeline](#-running-the-pipeline)
- [Dashboard Preview](#-dashboard-insights)
- [Exploring the Dashboard](#-exploring-the-dashboard)
- [Stopping Services](#-stopping-services)
- [Learning Outcomes](#-learning-outcomes)
---
## Overview

A **full-stack data engineering & analytics pipeline** that ingests raw e-commerce product and order data, stores it in a **MySQL database**, exposes data through a **Flask REST API**, and visualizes insights using an **interactive Streamlit dashboard**.

This project demonstrates **end-to-end data flow** — from ingestion → storage → API → analytics — using production-style Python tools.

---


## 📌 Key Capabilities

- **Multi-Source Product Ingestion**
  - Aggregates product data from multiple JSON sources
  - Harmonizes schemas and removes inconsistencies

- **Order Data Processing**
  - Ingests order data from CSV
  - Maintains referential integrity between products, orders, and order items

- **REST API Layer**
  - Flask-based API serving product data
  - Simulates an external upstream data provider

- **Analytics Dashboard**
  - Streamlit web app for sales analysis and product performance
  - Interactive charts and KPIs

- **Relational Database Backend**
  - MySQL (MariaDB) as a centralized data store
  - Normalized schema with foreign-key constraints

---

## 🧱 System Architecture

```

┌────────────────────┐
│ JSON Product Feeds │
└─────────┬──────────┘
│
┌─────────▼──────────┐
│ Flask REST API     │
└─────────┬──────────┘
│
┌─────────▼──────────┐
│ Data Ingestion     │
│ (Pandas + Python)  │
└─────────┬──────────┘
│
┌─────────▼──────────┐
│ MySQL Database     │
│ (Products, Orders) │
└─────────┬──────────┘
│
┌─────────▼──────────┐
│ Streamlit Dashboard│
└────────────────────┘

````

---

## 🛠️ Technologies Used

| Layer | Tools |
|-----|------|
| Language | Python 3.8+ |
| API | Flask |
| Analytics | Streamlit |
| Data Processing | Pandas |
| Database | MySQL / MariaDB |
| DB Connector | mysql-connector-python / PyMySQL |
| Server | XAMPP |
| Visualization | Streamlit Charts |

---

## 📂 Project Structure

```text
/Ecommerce_Data_Analyzer/
│
├── api_server.py          # Flask REST API
├── data_ingestion.py      # Product & order ingestion
├── app.py                 # Streamlit dashboard
│
├── data/
│   ├── products_source_1.json
│   ├── products_source_2.json
│   └── orders.csv
│
├── mysql_setup.sql        # DB schema
├── requirements.txt
└── README.md
````

---

## 📦 Prerequisites

* **Python 3.8+**
* **XAMPP** (Apache + MySQL + phpMyAdmin)
* Basic knowledge of SQL & Python virtual environments

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone <your-repository-url>
cd Ecommerce_Data_Analyzer
```

---

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv .venv
```

**Windows**

```bash
.\.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ MySQL Database Setup

1. Launch **XAMPP**
2. Start **Apache** and **MySQL**
3. Open **phpMyAdmin** → `http://localhost/phpmyadmin`
4. Open **SQL tab**
5. Paste contents of `mysql_setup.sql`
6. Execute to create:

   * `products`
   * `orders`
   * `order_items`

> ⚠️ If MySQL runs on a non-default port (e.g. `3307`), update it in Python configs.

---

## 🔐 Database Configuration

Update `DB_CONFIG` in:

* `api_server.py`
* `data_ingestion.py`
* `app.py`

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ecommerce_data',
    'user': 'root',
    'password': '',
    'port': 3306
}
```

---

## 📊 Data Integrity Requirement

Ensure **all product IDs referenced in `orders.csv` exist** in the product JSON files.

Missing product definitions will cause **foreign-key constraint errors**.

---

## ▶ Running the Pipeline

### 1️⃣ Start Flask API

```bash
python api_server.py
```

📍 Runs at: `http://127.0.0.1:5000`

---

### 2️⃣ Run Data Ingestion

```bash
python data_ingestion.py
```

✔ Inserts products & orders into MySQL

---

### 3️⃣ Launch Streamlit Dashboard

```bash
streamlit run app.py
```

📍 Opens at: `http://localhost:8501`

---

## 📈 Dashboard Preview

### Performance Overview

![Performance Overview](https://github.com/Quantamaster/Ecommerce_Data_Analyzer/blob/main/performance%20overview%20chart.png)

### Dashboard

![Dashboard](https://github.com/Quantamaster/Ecommerce_Data_Analyzer/blob/main/Dashboard.png)

---

## 🔍 Dashboard Insights

* Sales trends over time
* Product-level revenue analysis
* Category & brand performance
* Order volume statistics

---

## 🛑 Stopping Services

* Press `Ctrl + C` in terminals running:

  * `api_server.py`
  * `app.py`
* Stop MySQL & Apache via XAMPP

---

## 🎯 Learning Outcomes

* Designing **end-to-end data pipelines**
* Working with **relational databases**
* Building **REST APIs**
* Creating **interactive analytics dashboards**
* Enforcing **data integrity constraints**

---

⭐ If this project helped you learn or build, consider starring the repository!










