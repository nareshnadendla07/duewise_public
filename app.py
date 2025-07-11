import streamlit as st
import pandas as pd
from modules.parse_financials import parse_financial_data, extract_text_from_image
from modules.extract_metrics import extract_key_metrics
from modules.results import generate_financial_verdict
from modules.pdf_report import create_pdf_report
from modules.email_report import send_email_with_report
from modules.verdict_utils import render_verdict_box
from dotenv import load_dotenv
import tempfile
import openai
import os
import base64
from bs4 import BeautifulSoup

def get_base64_logo(path):
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

# Corrected path to your logo file
logo_data_url = get_base64_logo("static/images/DueWiseLogo.png")


# Header section
with st.container():
    st.markdown(f"""
    <div style="padding: 1rem 0 1rem 0;">
      <div style="display: flex; align-items: center;">
        <img src="{logo_data_url}" width="250" style="margin-right: 1.5rem;">
        <div>
          <h1 style="margin-bottom: 0; font-size: 1.8rem;">
            <span style="font-weight: 600;">DueWise</span> – 
            <span style="color:#1F4E79;">AI-Powered Financial Statement Analyzer</span>
          </h1>
          <p style="margin-top: 0.2rem; font-size: 0.95rem; color: grey;">
            Upload financial PDFs or images to extract metrics and generate insights using AI.
          </p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# Load environment
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Upload files
uploaded_files = st.file_uploader(
    "Upload PDFs or scanned images", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True
)

combined_text = ""
combined_tables = []
temp_files_to_delete = []
file_summary = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_type = "Image" if uploaded_file.type.startswith("image/") else "PDF"
        icon = "🖼" if file_type == "Image" else "📄"
        status = ""

        suffix = "." + uploaded_file.type.split("/")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
            temp_files_to_delete.append(temp_path)

        with st.spinner(f"{icon} Processing `{uploaded_file.name}`..."):
            if file_type == "Image":
                extracted_text = extract_text_from_image(temp_path)
                combined_text += extracted_text + "\n\n"
                status = "🧠 OCR Scanned"
            else:
                result = parse_financial_data(temp_path)
                combined_text += result["raw_text"] + "\n\n"
                combined_tables.extend(result["tables"])
                status = "✅ Parsed"

        file_summary.append({
            "File Name": uploaded_file.name,
            "Type": file_type,
            "Status": status
        })

    # Show file summary
    st.markdown("### 🧾 File Processing Summary")
    summary_df = pd.DataFrame(file_summary)
    summary_df.index += 1
    st.table(summary_df)

    # Show merged tables
    st.subheader("📊 Combined Tables")
    if combined_tables:
        merged_table = pd.concat(combined_tables, ignore_index=True)
        st.dataframe(merged_table, use_container_width=True)
    else:
        st.warning("No tables extracted from the PDFs or images.")

    # Show raw text preview
    st.subheader("📄 Combined Raw Text Preview")
    st.text_area("Combined Raw Text", combined_text[:3000], height=200)

    # Extract financial metrics
    metrics = extract_key_metrics(combined_text, combined_tables)

    # Display metrics
    # Descriptions for tooltips
    metric_tooltips = {
        "total_revenue": "Total earnings from sales or services before expenses.",
        "average_weekly_sales": "Mean weekly sales revenue across the business period.",
        "cogs": "Cost of Goods Sold – direct production or service delivery costs.",
        "advertising": "Expenses related to marketing and promotions.",
        "wages": "Employee salaries and related labor costs.",
        "rent": "Monthly or annual business rental costs.",
        "net_profit": "Total earnings after subtracting all expenses.",
        "cleaning": "Costs for maintaining hygiene and cleanliness (if any)."
    }

    st.subheader("📌 Combined Financial Metrics (editable)")
    for key, value in metrics.items():
        label = f"**{key.replace('_', ' ').title()}**"
        tooltip = metric_tooltips.get(key, "")
        if value is None:
            st.markdown(f"- {label} <span title='{tooltip}' style='color:gray;'>ℹ️</span>", unsafe_allow_html=True)
            new_val = st.text_input(
                label="",  # No label to prevent line above
                placeholder="Enter a value (e.g. 1000)",
                help=tooltip,
                key=f"{key}_merged"
            )
            if new_val.strip().replace(",", "").replace("$", "").replace(".", "").isdigit():
                metrics[key] = float(new_val.replace(",", "").replace("$", ""))
        else:
            st.markdown(f"- {label}: {value} <span title='{tooltip}' style='color:gray;'>ℹ️</span>", unsafe_allow_html=True)

    # Show button only when there's valid input
    custom_btn = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #1F4E79;
            color: white;
            font-weight: 500;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
        }
        div.stButton > button:first-child:hover {
            background-color: #163a5c;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("📈 Generate Combined Financial Verdict"):
        with st.spinner("Analyzing across all files..."):
            verdict = generate_financial_verdict(metrics)

            # Render HTML-styled verdict
            styled_html = render_verdict_box(verdict)

            # Load HTML template and inject the verdict content
            with open("templates/duewise_ui_template.html", "r", encoding="utf-8") as f:
                html_template = f.read()
            full_html = (
                html_template
                .replace("{{ verdict_content }}", styled_html)
                .replace("{{ logo_url }}", logo_data_url)  # ← Inject base64 logo
            )

            # Display the verdict inside the full styled HTML shell
            st.subheader("📋 Combined Verdict & Suggestions")
            st.components.v1.html(full_html, height=600, scrolling=True)

            # Generate PDF using raw verdict text (not HTML for now)
            report_path = "DueWise_Combined_Report.pdf"
            create_pdf_report(metrics, verdict, filename=report_path)

            # Download + Email options
            with open(report_path, "rb") as f:
                st.download_button(
                    label="📤 Download Combined Report",
                    data=f,
                    file_name=report_path,
                    mime="application/pdf"
                )

            with st.expander("📧 Email this Report"):
                email = st.text_input("Recipient Email")
                if st.button("Send Email Report"):
                    if email:
                        if send_email_with_report(email, report_path):
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error("❌ Failed to send the email.")
                    else:
                        st.warning("Please enter a valid email address.")

            try:
                os.remove(report_path)
            except:
                pass

    # Clean up all temp files
    for path in temp_files_to_delete:
        try:
            os.remove(path)
        except Exception as e:
            print(f"❌ Failed to delete temp file: {path} — {e}")
else:
    st.info("📂 Upload one or more PDF/image files to begin analysis.")
