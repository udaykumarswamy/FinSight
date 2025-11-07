from typing import Dict, List, Union, Optional, Tuple
import re
from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class PlottableData:
    title: str
    x_label: str
    y_label: str
    data: Dict[str, Union[float, int]]
    interval: Optional[str] = None  # store the detected interval type

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

def extract_numeric_data(text: str) -> Optional[PlottableData]:
    """Extract plottable numeric data from text with dynamic time intervals."""
    # Detect time format and interval
    time_format, interval = detect_time_pattern(text)
    
    # Dynamic pattern based on detected interval
    patterns = {
        'minute': r'(\d{2}:\d{2}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'hour': r'(\d{2}:00).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
        'day': r'(\d{2}/\d{2}).*?(?:Close|Price|Value)[\s:]+([\d,.]+)',
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
    
    title = f"{''.join(word.capitalize() for word in interval.split('_'))}ly Price Movement"
    return PlottableData(
        title=title,
        x_label=x_label,
        y_label=y_label,
        data=dict(sorted(data.items())),  # ensure chronological order
        interval=interval
    )
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
    
def plot_ascii(data: PlottableData, width: int = 80, height: int = 20):
    """Generate ASCII plot with dynamic formatting based on interval."""
    if not data.data:
        return "No plottable data found."

    # Calculate scale with padding
    values = list(data.data.values())
    max_val = max(values)
    min_val = min(values)
    padding = (max_val - min_val) * 0.1
    max_val += padding
    min_val -= padding
    scale = (height - 1) / (max_val - min_val) if max_val != min_val else 1

    # Create canvas with grid
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw grid
    for i in range(height):
        canvas[i][0] = '│'
        if i % 4 == 0:  # horizontal grid lines
            for j in range(width):
                if canvas[i][j] == ' ':
                    canvas[i][j] = '·'
    for i in range(width):
        canvas[-1][i] = '─'
        if i % 10 == 0:  # vertical grid lines
            for j in range(height):
                if canvas[j][i] == ' ':
                    canvas[j][i] = '·'
    canvas[-1][0] = '└'

    # Plot points and lines
    x_scale = (width - 2) / (len(data.data) - 1) if len(data.data) > 1 else 1
    sorted_items = sorted(data.data.items())
    
    # Draw points and trend lines
    prev_x, prev_y = None, None
    for i, (label, value) in enumerate(sorted_items):
        x = int(1 + i * x_scale)
        y = int(height - 1 - (value - min_val) * scale)
        
        # Draw point
        canvas[y][x] = '●'
        
        # Draw connecting lines with trend indicators
        if prev_x is not None:
            for px in range(prev_x + 1, x):
                py = int(prev_y + (y - prev_y) * (px - prev_x) / (x - prev_x))
                if y < prev_y:
                    canvas[py][px] = '╱'  # upward trend
                elif y > prev_y:
                    canvas[py][px] = '╲'  # downward trend
                else:
                    canvas[py][px] = '─'  # flat
        
        prev_x, prev_y = x, y

    # Format labels based on interval
    result = [f"\n{data.title}\n"]
    
    # Y-axis labels with appropriate precision
    precision = 2 if "Price" in data.y_label else 1
    y_values = [min_val + (max_val - min_val) * i / (height - 1) for i in range(height)]
    y_values.reverse()
    
    # Draw plot with labels
    for i, row in enumerate(canvas):
        if i % 4 == 0:
            label = f"{y_values[i]:.{precision}f}"
            result.append(f"{label:>8} ┤" + "".join(row[1:]))
        else:
            result.append(" " * 8 + "│" + "".join(row[1:]))
    
    # X-axis labels with dynamic formatting
    x_labels = []
    for label, _ in sorted_items:
        if data.interval == 'hour':
            x_labels.append(f"{label:>5}")
        elif data.interval == 'minute':
            x_labels.append(label[-5:])  # show only MM:SS
        else:
            x_labels.append(f"{label:>5}")
    
    # Add x-axis
    label_positions = [int(1 + i * x_scale) for i in range(len(x_labels))]
    x_axis = " " * 8 + "└" + "─" * (width - 1)
    x_labels_line = " " * 8 + " " + " ".join(
        " " * (pos - len(x_axis) + 1) + label 
        for pos, label in zip(label_positions, x_labels)
    )
    
    result.extend([x_axis, x_labels_line])
    result.append(f"\n{data.x_label} vs {data.y_label}\n")
    
    return "\n".join(result)


def try_plot_from_text(text: str) -> Optional[str]:
    """Try to extract and plot data from text if possible."""
    #adding logger to this function is not necessary as per current requirements
    print("Attempting to extract plottable data from text...")
    data = extract_numeric_data(text)
    if data:
        return plot_ascii(data)
    return None