from typing import Dict, List, Union, Optional, Tuple
import re
import json
from dataclasses import dataclass, asdict

@dataclass
class PlottableData:
    title: str
    x_label: str
    y_label: str
    data: Dict[str, Union[float, int]]
    interval: Optional[str] = None  # store the detected interval type
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "labels": list(self.data.keys()),
            "values": list(self.data.values()),
            "interval": self.interval
        }

def detect_time_pattern(text: str) -> Tuple[str, str]:
    """Detect the time pattern and interval in the text.

    Returns (time_format, interval). We prioritize more specific patterns
    (quarters, exact hourly markers like '09:00') before generic minute matches
    so '09:00' is classified as an hour interval (hourly series) instead of
    minute series.
    """
    # Quarter first (most specific)
    if re.search(r'\bQ\d\s+\d{4}\b', text, re.IGNORECASE):
        return '%Y-Q', 'quarter'  # custom marker for quarter parsing

    # Year
    if re.search(r'\b\d{4}\b', text) and not re.search(r'\b\d{2}:\d{2}\b', text):
        return '%Y', 'year'

    # Day (MM/DD) next
    if re.search(r'\b\d{1,2}/\d{1,2}\b', text):
        return '%m/%d', 'day'

    # If we have time-like tokens HH:MM
    if re.search(r'\b\d{1,2}:\d{2}\b', text):
        # If most or many matches are on the hour (":00") treat as hourly series
        matches = re.findall(r'\b\d{1,2}:\d{2}\b', text)
        if matches:
            hour_matches = sum(1 for m in matches if m.endswith(':00'))
            # if more than half are :00, classify as hourly (common case)
            if hour_matches >= max(1, len(matches) // 2):
                return '%H:%M', 'hour'
            return '%H:%M', 'minute'

    # Fallback: minute format
    return '%H:%M', 'minute'

def parse_time_value(time_str: str, fmt: str) -> str:
    """Normalize time strings so sorting is chronological and keys are readable.

    - For minutes/hours (fmt '%H:%M') keep zero-padded 'HH:MM' (24h).
    - For days use MM/DD as-is converted to zero-padded 'MM/DD'.
    - For quarters use 'YYYY-Qn'.
    - For years keep 'YYYY'.
    """
    try:
        if fmt == '%Y-Q':
            # time_str like "Q2 2024" or "Q2 2024:" -> extract quarter and year
            q = re.search(r'Q(\d)', time_str, re.IGNORECASE)
            y = re.search(r'(\d{4})', time_str)
            if q and y:
                return f"{y.group(1)}-Q{q.group(1)}"
            return time_str.strip()
        if fmt == '%H:%M':
            # normalize to zero-padded HH:MM
            m = re.match(r'(\d{1,2}):(\d{2})', time_str)
            if m:
                hh = int(m.group(1))
                mm = int(m.group(2))
                return f"{hh:02d}:{mm:02d}"
            return time_str.strip()
        if fmt == '%m/%d':
            m = re.match(r'(\d{1,2})/(\d{1,2})', time_str)
            if m:
                mm = int(m.group(1))
                dd = int(m.group(2))
                return f"{mm:02d}/{dd:02d}"
        if fmt == '%Y':
            y = re.search(r'(\d{4})', time_str)
            return y.group(1) if y else time_str.strip()
        return time_str.strip()
    except Exception:
        return time_str.strip()
    
    
def extract_numeric_data(text: str) -> Optional[PlottableData]:
    """Extract plottable numeric data from text with dynamic time intervals."""
    # Detect time format and interval
    time_format, interval = detect_time_pattern(text)
    
    # Dynamic pattern based on detected interval
    patterns = {
        'minute': r'(\d{1,2}:\d{2}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'hour': r'(\d{1,2}:\d{2}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'day': r'(\d{1,2}/\d{1,2}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'quarter': r'(Q\d\s+\d{4}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'year': r'(\d{4}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)[Bb]?illion?',
    }
    
    pattern = patterns.get(interval)
    if not pattern:
        return None
        
    matches = re.findall(pattern, text, re.IGNORECASE)
    if not matches:
        return None
        
    # Parse and sort data
    data = {}
    for time_str, value in matches:
        key = parse_time_value(time_str, time_format)
        try:
            data[key] = float(value.replace(',', ''))
        except ValueError:
            continue
    
    if not data:
        return None
    
    # Create appropriate labels based on interval
    labels = {
        'minute': ('Time (Minutes)', 'Price ($)'),
        'hour': ('Time (Hours)', 'Price ($)'),
        'day': ('Date', 'Price ($)'),
        'quarter': ('Quarter', 'Value ($B)'),
        'year': ('Year', 'Value ($B)')
    }
    x_label, y_label = labels.get(interval, ('Time', 'Value'))
    
    # friendly title mapping
    title_map = {
        'minute': 'Minutely Price Movement',
        'hour': 'Hourly Price Movement',
        'day': 'Daily Price Movement',
        'quarter': 'Quarterly Price Movement',
        'year': 'Yearly Price Movement'
    }
    title = title_map.get(interval, 'Price Movement')
    return PlottableData(
        title=title,
        x_label=x_label,
        y_label=y_label,
        data=dict(sorted(data.items())),  # ensure chronological order
        interval=interval
    )
    
def try_plot_from_text(text: str) -> Optional[Dict]:
    """
    Try to extract plottable data from text and return as structured data for web visualization.
    Returns a dictionary with chart configuration for Chart.js or None if no data found.
    """
    data = extract_numeric_data(text)
    if data and data.data:
        return data.to_dict()
    return None