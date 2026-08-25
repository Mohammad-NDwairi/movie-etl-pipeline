"""Automated ETL Pipeline: Top 50 Ranked Films.

This script extracts top-ranked movie data from an archived web page,
transforms data types, and loads the structured output into both a CSV file
and an SQLite database table.
"""

from datetime import datetime
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import requests

# ==============================================================================
# Configuration & Global Constants
# ==============================================================================
# Source URL for web scraping (Archived Wikipedia/EverybodyWiki page)
SOURCE_URL = 'https://web.archive.org/web/20230902185655/https://en.everybodywiki.com/100_Most_Highly-Ranked_Films'

# Database and file path targets
DATABASE_NAME = 'Movies.db'
TABLE_NAME = 'Top_50'
CSV_OUTPUT_PATH = 'top_50_films.csv'
LOG_FILE_PATH = 'code_log.txt'


# ==============================================================================
# Pipeline Functions
# ==============================================================================
def log_progress(message: str) -> None:
  """Appends a timestamped log entry to the log file and prints to stdout.

  Args:
      message (str): Description of the milestone or event to record.
  """
  timestamp_format = '%Y-%b-%d-%H:%M:%S'
  now = datetime.now()
  timestamp = now.strftime(timestamp_format)

  # Append log entry to disk
  with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
    f.write(f'{timestamp} : {message}\n')

  # Output log message to terminal for real-time tracking
  print(f'[{timestamp}] {message}')


def extract(url: str) -> pd.DataFrame:
  """Extracts the top 50 movie records from the specified webpage table.

  Args:
      url (str): The web link from which to scrape data.

  Returns:
      pd.DataFrame: Raw dataframe containing extracted rows.
  """
  # Send HTTP GET request to fetch web page content
  response = requests.get(url, timeout=15)
  response.raise_for_status()

  # Parse HTML response using BeautifulSoup DOM parser
  soup = BeautifulSoup(response.text, 'html.parser')

  # Locate table bodies and extract table rows
  tables = soup.find_all('tbody')
  rows = tables[0].find_all('tr')

  extracted_records = []
  count = 0

  # Iterate over rows to extract table cells up to top 50 records
  for row in rows:
    if count >= 50:
      break

    cols = row.find_all('td')

    # Ensure the row contains valid data columns (skip header/empty rows)
    if len(cols) >= 3:
      # Use .get_text(strip=True) to safely parse inner text and clean whitespaces
      rank = cols[0].get_text(strip=True)
      film = cols[1].get_text(strip=True)
      year = cols[2].get_text(strip=True)

      extracted_records.append(
          {'Average Rank': rank, 'Film': film, 'Year': year}
      )
      count += 1

  # Convert extracted list of dictionaries into a Pandas DataFrame
  return pd.DataFrame(extracted_records)


def transform(df: pd.DataFrame) -> pd.DataFrame:
  """Performs data cleaning and enforces strict data types.

  Args:
      df (pd.DataFrame): Raw DataFrame from extraction phase.

  Returns:
      pd.DataFrame: Cleaned DataFrame with integer types for Rank and Year.
  """
  # Enforce numeric schema conversion for analytical workloads
  df['Average Rank'] = df['Average Rank'].astype(int)
  df['Year'] = df['Year'].astype(int)

  return df


def load_to_csv(df: pd.DataFrame, target_path: str) -> None:
  """Saves the transformed DataFrame to a CSV flat file.

  Args:
      df (pd.DataFrame): Transformed DataFrame.
      target_path (str): Destination file system path.
  """
  df.to_csv(target_path, index=False)


def load_to_db(df: pd.DataFrame, conn: sqlite3.Connection, table: str) -> None:
  """Loads the structured DataFrame into an SQLite database table.

  Args:
      df (pd.DataFrame): Transformed DataFrame.
      conn (sqlite3.Connection): Active SQLite connection instance.
      table (str): Target table name inside the database.
  """
  df.to_sql(table, conn, if_exists='replace', index=False)


# ==============================================================================
# Main ETL Driver
# ==============================================================================
if __name__ == '__main__':
  log_progress('ETL Job Initialized')

  # --------------------------------------------------------------------------
  # 1. Extraction Phase
  # --------------------------------------------------------------------------
  log_progress('Extraction phase: Started')
  raw_dataframe = extract(SOURCE_URL)
  log_progress(
      f'Extraction phase: Completed ({len(raw_dataframe)} records retrieved)'
  )

  # --------------------------------------------------------------------------
  # 2. Transformation Phase
  # --------------------------------------------------------------------------
  log_progress('Transformation phase: Started')
  cleaned_dataframe = transform(raw_dataframe)
  log_progress('Transformation phase: Completed')

  # --------------------------------------------------------------------------
  # 3. Loading to Flat File (CSV)
  # --------------------------------------------------------------------------
  log_progress('Load to CSV phase: Started')
  load_to_csv(cleaned_dataframe, CSV_OUTPUT_PATH)
  log_progress(f'Load to CSV phase: Completed -> {CSV_OUTPUT_PATH}')

  # --------------------------------------------------------------------------
  # 4. Loading to Relational Database (SQLite)
  # --------------------------------------------------------------------------
  log_progress('Load to Database phase: Started')
  db_connection = sqlite3.connect(DATABASE_NAME)

  load_to_db(cleaned_dataframe, db_connection, TABLE_NAME)
  log_progress(
      f'Load to Database phase: Completed -> {DATABASE_NAME} [{TABLE_NAME}]'
  )

  # --------------------------------------------------------------------------
  # 5. Data Validation & Verification Query
  # --------------------------------------------------------------------------
  log_progress('Validation query: Executing sample verification query')
  verification_query = (
      f'SELECT Film, Year FROM {TABLE_NAME} WHERE Year > 2000 LIMIT 5'
  )
  verification_result = pd.read_sql(verification_query, db_connection)

  print('\n=== Verification Output: Movies Released After 2000 ===')
  print(verification_result.to_string(index=False))
  print('=======================================================\n')

  # Close database connection and wrap up
  db_connection.close()
  log_progress('ETL Job Terminated Successfully')