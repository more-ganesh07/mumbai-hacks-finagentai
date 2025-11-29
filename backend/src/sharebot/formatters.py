"""
Response Formatting Utilities for ShareBot
Lightweight helpers for professional fintech-style output
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


# -------------------------------------------------------------------------
# Number Formatting
# -------------------------------------------------------------------------

def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with Indian numbering system and abbreviations
    
    Examples:
        1234.56 -> 1,234.56
        1234567 -> 12.35L
        12345678 -> 1.23Cr
    """
    try:
        value = float(value)
        
        # Handle very large numbers
        if abs(value) >= 10000000:  # 1 Crore
            return f"{value / 10000000:.2f}Cr"
        elif abs(value) >= 100000:  # 1 Lakh
            return f"{value / 100000:.2f}L"
        elif abs(value) >= 1000:  # Thousands
            return f"{value / 1000:.2f}K"
        else:
            return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(value: float, symbol: str = "₹", decimals: int = 2) -> str:
    """
    Format currency with symbol
    
    Examples:
        2456.75 -> ₹2,456.75
        1234567 -> ₹12.35L
    """
    try:
        value = float(value)
        formatted = format_number(value, decimals)
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: float, decimals: int = 2, include_sign: bool = True) -> str:
    """
    Format percentage with sign
    
    Examples:
        2.34 -> +2.34%
        -1.56 -> -1.56%
    """
    try:
        value = float(value)
        sign = "+" if value > 0 and include_sign else ""
        return f"{sign}{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_change(value: float, percentage: float) -> str:
    """
    Format price change with indicator
    
    Examples:
        (56.20, 2.34) -> 🔺 +2.34% (+₹56.20)
        (-23.45, -1.56) -> 🔻 -1.56% (-₹23.45)
    """
    try:
        value = float(value)
        percentage = float(percentage)
        
        indicator = "🔺" if value >= 0 else "🔻"
        sign = "+" if value > 0 else ""
        
        return f"{indicator} {format_percentage(percentage)} ({sign}{format_currency(value)})"
    except (ValueError, TypeError):
        return "N/A"


def format_volume(value: float) -> str:
    """
    Format trading volume
    
    Examples:
        1234567 -> 1.23M
        12345678901 -> 12.35B
    """
    try:
        value = float(value)
        
        if abs(value) >= 1_000_000_000_000:  # Trillion
            return f"{value / 1_000_000_000_000:.2f}T"
        elif abs(value) >= 1_000_000_000:  # Billion
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:  # Million
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:  # Thousand
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:,.0f}"
    except (ValueError, TypeError):
        return "N/A"


# -------------------------------------------------------------------------
# Date/Time Formatting
# -------------------------------------------------------------------------

def format_datetime(dt: Any, format_str: str = "%d %b %Y, %I:%M %p") -> str:
    """
    Format datetime object
    
    Examples:
        datetime(2024, 1, 15, 14, 30) -> "15 Jan 2024, 02:30 PM"
    """
    try:
        if isinstance(dt, str):
            # Try to parse string to datetime
            dt = pd.to_datetime(dt)
        
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        
        if isinstance(dt, datetime):
            return dt.strftime(format_str)
        
        return str(dt)
    except Exception:
        return "N/A"


def format_date(dt: Any) -> str:
    """Format date only"""
    return format_datetime(dt, "%d %b %Y")


# -------------------------------------------------------------------------
# Markdown Table Generation
# -------------------------------------------------------------------------

def dataframe_to_markdown(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Convert DataFrame to markdown table
    
    Args:
        df: DataFrame to convert
        max_rows: Maximum rows to include (default 10)
    
    Returns:
        Markdown formatted table string
    """
    if df is None or df.empty:
        return "_No data available_"
    
    try:
        # Limit rows
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        # Convert to markdown
        return df.to_markdown(index=False)
    except Exception as e:
        return f"_Error formatting table: {str(e)}_"


def dict_to_markdown_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    """
    Convert list of dictionaries to markdown table
    
    Args:
        data: List of dictionaries with same keys
        headers: Optional custom headers (defaults to dict keys)
    
    Returns:
        Markdown formatted table string
    """
    if not data:
        return "_No data available_"
    
    try:
        # Get headers
        if headers is None:
            headers = list(data[0].keys())
        
        # Build table
        lines = []
        
        # Header row
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        
        # Separator row
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        
        # Data rows
        for row in data:
            values = [str(row.get(h, "N/A")) for h in headers]
            lines.append("| " + " | ".join(values) + " |")
        
        return "\n".join(lines)
    except Exception as e:
        return f"_Error formatting table: {str(e)}_"


def create_key_value_table(data: Dict[str, Any]) -> str:
    """
    Create a simple key-value markdown table
    
    Args:
        data: Dictionary of key-value pairs
    
    Returns:
        Markdown formatted table string
    """
    if not data:
        return "_No data available_"
    
    try:
        lines = []
        lines.append("| Metric | Value |")
        lines.append("| ------ | ----- |")
        
        for key, value in data.items():
            # Format value based on type
            if isinstance(value, float):
                if abs(value) > 1000:
                    formatted_value = format_number(value)
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            lines.append(f"| {key} | {formatted_value} |")
        
        return "\n".join(lines)
    except Exception as e:
        return f"_Error formatting table: {str(e)}_"


# -------------------------------------------------------------------------
# Visual Indicators
# -------------------------------------------------------------------------

def get_trend_indicator(value: float) -> str:
    """
    Get trend indicator emoji
    
    Returns:
        🔺 for positive, 🔻 for negative, ➖ for neutral
    """
    try:
        value = float(value)
        if value > 0:
            return "🔺"
        elif value < 0:
            return "🔻"
        else:
            return "➖"
    except (ValueError, TypeError):
        return "➖"


def get_sentiment_indicator(value: float, thresholds: tuple = (30, 70)) -> str:
    """
    Get sentiment indicator based on value and thresholds
    
    Args:
        value: Numeric value (e.g., RSI)
        thresholds: (low, high) thresholds
    
    Returns:
        Emoji indicator
    """
    try:
        value = float(value)
        low, high = thresholds
        
        if value < low:
            return "🔴"  # Oversold/Bearish
        elif value > high:
            return "🟢"  # Overbought/Bullish
        else:
            return "🟡"  # Neutral
    except (ValueError, TypeError):
        return "⚪"


# -------------------------------------------------------------------------
# Response Formatting
# -------------------------------------------------------------------------

def format_stock_price(symbol: str, price: float, change: float, change_pct: float) -> str:
    """
    Format stock price with change indicator
    
    Returns:
        **Symbol**: ₹price 🔺 +change% (+₹change)
    """
    try:
        indicator = get_trend_indicator(change)
        price_str = format_currency(price)
        change_str = format_currency(abs(change))
        pct_str = format_percentage(change_pct)
        sign = "+" if change >= 0 else "-"
        
        return f"**{symbol}**: {price_str} {indicator} {pct_str} ({sign}{change_str})"
    except Exception:
        return f"**{symbol}**: Price unavailable"


def format_error_message(error: str, context: str = "") -> str:
    """
    Format user-friendly error message
    
    Args:
        error: Error description
        context: Optional context
    
    Returns:
        Formatted error message
    """
    if context:
        return f"⚠️ **Unable to fetch {context}**: {error}\n\nPlease try again or check the symbol."
    else:
        return f"⚠️ **Error**: {error}\n\nPlease try again."


def format_partial_result(available_data: str, missing_data: str) -> str:
    """
    Format partial result message when some tools fail
    
    Args:
        available_data: Description of available data
        missing_data: Description of missing data
    
    Returns:
        Formatted message
    """
    return f"ℹ️ **Partial data available**: {available_data}\n\n_Note: {missing_data} could not be fetched at this time._"


# -------------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean text for markdown output
    
    - Remove extra whitespace
    - Handle special characters
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Escape pipe characters in tables
    text = text.replace("|", "\\|")
    
    return text


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to max length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
