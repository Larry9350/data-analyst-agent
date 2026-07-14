import pandas as pd
from tools.data_loader import query

def run_sql(sql: str) -> dict:
    """
    Execute a SQL query and return results in a clean format.
    The agent calls this to extract insights from the data.
    """
    try:
        df = query(sql)
        return {
            "success": True,
            "sql": sql,
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.to_dict(orient='records'),
            "dataframe": df
        }
    except Exception as e:
        return {
            "success": False,
            "sql": sql,
            "error": str(e),
            "data": [],
            "dataframe": pd.DataFrame()
        }


def run_multiple(queries: list[str]) -> list[dict]:
    """Run multiple SQL queries and return all results."""
    return [run_sql(q) for q in queries]


def summarize_result(result: dict) -> str:
    """
    Convert a SQL result into a human-readable string.
    This gets fed to the LLM so it can interpret the numbers.
    """
    if not result["success"]:
        return f"Query failed: {result['error']}"

    lines = [f"Query: {result['sql']}",
             f"Returned {result['rows']} rows\n"]

    df = result["dataframe"]
    if not df.empty:
        lines.append(df.to_string(index=False))

    return "\n".join(lines)