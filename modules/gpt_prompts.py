def generate_verdict_prompt(metrics_dict):
    return f"""
    Given the following metrics:
    - Current Ratio: {metrics_dict['current_ratio']}
    - Net Profit Margin: {metrics_dict['net_margin']}
    ...
    Provide a business health verdict, potential risks, and improvement suggestions.
    """
