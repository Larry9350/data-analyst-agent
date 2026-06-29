import duckdb
import pandas as pd
from pathlib import Path

# In-memory database - no server, no setup, instant
conn = duckdb.connect()

def load_csv(filepath: str) -> dict:
    """
    Load a CSV into DuckDB and return metadata.
    The agent uses this to understand the data before analyzing it.
    """
    path = Path(filepath)
    table_name = path.stem.replace("-", "_").replace(" ", "_")

    # DuckDB reads CSV directly - auto-detects column types
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_csv_auto('{filepath}')
    """)

    schema = conn.execute(f"DESCRIBE {table_name}").fetchdf()
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()

    # Stats for numeric columns only
    numeric_cols = schema[schema['column_type'].isin([
        'BIGINT', 'INTEGER', 'DOUBLE', 'FLOAT', 'DECIMAL', 'HUGEINT'
    ])]['column_name'].tolist()

    stats = {}
    for col in numeric_cols:
        result = conn.execute(f"""
            SELECT
                MIN("{col}") as min,
                MAX("{col}") as max,
                ROUND(AVG("{col}"), 2) as avg,
                ROUND(STDDEV("{col}"), 2) as std
            FROM {table_name}
        """).fetchdf()
        stats[col] = result.to_dict(orient='records')[0]

    return {
        "table_name": table_name,
        "row_count": row_count,
        "columns": schema[['column_name', 'column_type']].to_dict(orient='records'),
        "sample": sample.to_dict(orient='records'),
        "numeric_stats": stats
    }


def query(sql: str) -> pd.DataFrame:
    """Run any SQL query and return a DataFrame."""
    return conn.execute(sql).fetchdf()


def get_connection():
    """Return the DuckDB connection."""
    return conn