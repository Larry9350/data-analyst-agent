import ollama

def analyze_data_profile(data_profile: dict) -> str:
    """
    Send the data profile to Mistral and ask it to decide
    what analysis questions are worth answering.
    """
    # Build a readable description of the dataset
    col_descriptions = "\n".join([
        f"  - {col['column_name']} ({col['column_type']})"
        for col in data_profile['columns']
    ])

    stats_description = ""
    for col, stats in data_profile['numeric_stats'].items():
        stats_description += f"\n  - {col}: min={stats['min']}, max={stats['max']}, avg={stats['avg']}, std={stats['std']}"

    sample_rows = "\n".join([str(row) for row in data_profile['sample'][:3]])

    prompt = f"""You are a senior data analyst. You have been given a dataset with the following profile:

TABLE NAME: {data_profile['table_name']}
ROW COUNT: {data_profile['row_count']}

COLUMNS:
{col_descriptions}

NUMERIC STATISTICS:
{stats_description}

SAMPLE ROWS:
{sample_rows}

Based on this dataset, suggest exactly 4 specific SQL analysis questions that would provide valuable business insights.
Format your response as a numbered list like this:
1. [question]
2. [question]
3. [question]
4. [question]

Only output the numbered list. No explanations."""

    response = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']


def generate_sql_for_questions(questions: str, table_name: str, columns: list) -> str:
    """
    Ask Mistral to write SQL queries for each analysis question.
    """
    col_list = ", ".join([f"{c['column_name']} ({c['column_type']})" for c in columns])

    prompt = f"""You are a SQL expert. Write DuckDB SQL queries for the following analysis questions.

TABLE NAME: {table_name}
COLUMNS: {col_list}

QUESTIONS:
{questions}

Write one SQL query per question. Format your response exactly like this:
SQL1: SELECT ...
SQL2: SELECT ...
SQL3: SELECT ...
SQL4: SELECT ...

Rules:
- Use only the table and columns listed above
- Keep queries simple and correct
- Always use double quotes around column names with spaces
- Only output the SQL lines, nothing else"""

    response = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']


def generate_final_report(data_profile: dict, questions: str, sql_results: list) -> str:
    """
    Take all the analysis results and ask Mistral to write
    a complete plain-English business report.
    """
    results_text = ""
    for i, result in enumerate(sql_results):
        if result['success'] and result['data']:
            results_text += f"\nAnalysis {i+1}:\n"
            results_text += f"Query: {result['sql']}\n"
            results_text += f"Results: {result['data']}\n"

    prompt = f"""You are a senior data analyst writing a business intelligence report.

DATASET: {data_profile['table_name']} with {data_profile['row_count']} rows

ANALYSIS PERFORMED:
{questions}

RESULTS:
{results_text}

Write a professional business report with these sections:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points with specific numbers)
3. Trends and Patterns (what stands out)
4. Recommendations (3 actionable suggestions)

Be specific, use the actual numbers from the results, and keep it concise."""

    response = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']