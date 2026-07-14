import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("outputs/reports")

def make_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> str:
    """Create a bar chart and save it. Returns the file path."""
    fig = px.bar(df, x=x, y=y, title=title, color=x,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(showlegend=False, plot_bgcolor='white')
    path = OUTPUT_DIR / f"{title.replace(' ', '_').lower()}.html"
    fig.write_html(str(path))
    return str(path)


def make_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> str:
    """Create a line chart and save it. Returns the file path."""
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_layout(plot_bgcolor='white')
    path = OUTPUT_DIR / f"{title.replace(' ', '_').lower()}.html"
    fig.write_html(str(path))
    return str(path)


def make_pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> str:
    """Create a pie chart and save it. Returns the file path."""
    fig = px.pie(df, names=names, values=values, title=title)
    path = OUTPUT_DIR / f"{title.replace(' ', '_').lower()}.html"
    fig.write_html(str(path))
    return str(path)


def make_histogram(df: pd.DataFrame, column: str, title: str) -> str:
    """Create a histogram and save it. Returns the file path."""
    fig = px.histogram(df, x=column, title=title, nbins=20)
    fig.update_layout(plot_bgcolor='white')
    path = OUTPUT_DIR / f"{title.replace(' ', '_').lower()}.html"
    fig.write_html(str(path))
    return str(path)


def auto_chart(df: pd.DataFrame, title: str) -> str:
    """
    Automatically pick the best chart type based on the data shape.
    This is what the agent calls when it doesn't specify a chart type.
    """
    cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(include='object').columns.tolist()

    # If we have one text col and one number col → bar chart
    if len(text_cols) >= 1 and len(numeric_cols) >= 1:
        return make_bar_chart(df, text_cols[0], numeric_cols[0], title)

    # If we have two numeric cols → line chart
    elif len(numeric_cols) >= 2:
        return make_line_chart(df, cols[0], cols[1], title)

    # Fallback → histogram of first numeric col
    elif len(numeric_cols) == 1:
        return make_histogram(df, numeric_cols[0], title)

    return "Could not generate chart - no suitable columns found"