from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # ✅ This must be at the top!

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_financial_verdict(metrics):
    prompt = f"""
    A small business has the following financial metrics:

    - Total Revenue: {metrics.get('total_revenue')}
    - Average Weekly Sales: {metrics.get('average_weekly_sales')}
    - COGS: {metrics.get('cogs')}
    - Advertising Expense: {metrics.get('advertising')}
    - Cleaning Expense: {metrics.get('cleaning')}
    - Wages: {metrics.get('wages')}
    - Rent: {metrics.get('rent')}
    - Net Profit: {metrics.get('net_profit')}

    Based on these numbers, provide:
    1. A short financial health summary (1 paragraph)
    2. 2-3 key risks or red flags, if any
    3. 2-3 suggestions for improvement or action
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a financial due diligence assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=500
    )

    return response.choices[0].message.content
