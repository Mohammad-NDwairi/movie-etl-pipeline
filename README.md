# 🎬 Top 50 Movies ETL Pipeline

A lightweight, automated ETL (Extract, Transform, Load) data pipeline built with Python. This project was developed as part of my practical learning journey in **Data Engineering** (IBM Data Engineering Lab) to demonstrate end-to-end data pipeline fundamentals.

---

## 📌 Project Overview

This script automates the process of:
1. **Extracting** movie rankings from an archived web source using web scraping.
2. **Transforming** raw HTML table records into clean, structured data with proper types.
3. **Loading** the cleaned dataset into two targets: a flat `CSV` file and a relational `SQLite` database.
4. **Logging** every milestone of execution with precise timestamps.

---

## 🏗️ Pipeline Architecture

```text
[ Web Source (HTML) ]
          │
          ▼  (requests + BeautifulSoup)
   [ Extract Phase ] ──► Parse top 50 records from DOM table
          │
          ▼  (pandas)
  [ Transform Phase ] ──► Enforce integer data types (Rank, Year) & clean strings
          │
          ▼
   [ Load Phase ]
     ├──► CSV File: `top_50_films.csv`
     └──► SQLite Database: `Movies.db` (Table: `Top_50`)
          │
          ▼
  [ Validation Query ] ──► Verify records where Year > 2000