import os
import base64
import openai
import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

openai.api_key = st.secrets["OPENAI_API_KEY"]

# email_report.py
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_NAME = st.secrets.get("EMAIL_NAME", "DueWise AI")

def send_email_with_report(to_email, report_path, sender_email='no-reply@duewise.ai'):
    with open(report_path, "rb") as f:
        data = f.read()
        encoded_file = base64.b64encode(data).decode()

    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject='📊 Your DueWise Financial Analysis Report',
        html_content='<p>Attached is your financial report from DueWise.</p>'
    )
    attached_file = Attachment(
        FileContent(encoded_file),
        FileName("DueWise_Combined_Report.pdf"),
        FileType("application/pdf"),
        Disposition("attachment")
    )
    message.attachment = attached_file

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False
