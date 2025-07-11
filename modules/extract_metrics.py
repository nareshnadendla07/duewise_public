import re

def extract_metric_from_text(text, keywords):
    lines = text.splitlines()
    for line in lines:
        for keyword in keywords:
            if keyword.lower() in line.lower():
                matches = re.findall(r"[-+]?\$?\d[\d,]*\.?\d*", line)
                if matches:
                    # Return first number found after the keyword
                    return float(matches[-1].replace('$', '').replace(',', ''))
    return None

def extract_metric_from_tables(tables, keyword_variants):
    for df in tables:
        for _, row in df.iterrows():
            for keyword in keyword_variants:
                for cell in row:
                    if isinstance(cell, str) and keyword.lower() in cell.lower():
                        # Try to find a number in the row
                        for item in row:
                            if isinstance(item, str):
                                match = re.findall(r"[\$]?\d[\d,]*\.?\d*", item)
                                if match:
                                    return float(match[0].replace("$", "").replace(",", ""))
    return None

def extract_key_metrics(raw_text, tables=None):
    return {
        "total_revenue": extract_metric_from_text(raw_text, ["total revenue", "total sales", "gross income"]) or (
            extract_metric_from_tables(tables, ["total sales"]) if tables else None),
        "average_weekly_sales": extract_metric_from_text(raw_text, ["average per week"]),
        "cogs": extract_metric_from_text(raw_text, ["cost of goods sold"]),
        "advertising": extract_metric_from_text(raw_text, ["advertising"]),
        "cleaning": extract_metric_from_text(raw_text, ["cleaning", "laundry"]),
        "wages": extract_metric_from_text(raw_text, ["wages", "salary"]) or (
            extract_metric_from_tables(tables, ["total wages", "total salary"]) if tables else None),
        "rent": extract_metric_from_text(raw_text, ["rent", "accommodation"]),
        "net_profit": extract_metric_from_text(raw_text, ["net profit", "adjusted net profit"]),
    }

