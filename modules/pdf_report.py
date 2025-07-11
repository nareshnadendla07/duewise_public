from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "DueWise Financial Review Report", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(5)

    def add_metrics(self, metrics):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Extracted Financial Metrics", ln=True)
        self.set_font("Arial", "", 11)
        for k, v in metrics.items():
            self.cell(0, 10, f"{k.title().replace('_',' ')}: {v}", ln=True)

    def add_verdict(self, verdict):
        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AI Verdict & Suggestions", ln=True)
        self.set_font("Arial", "", 11)
        for line in verdict.split("\n"):
            self.multi_cell(0, 10, line)

def create_pdf_report(metrics, verdict, filename="duewise_report.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.add_metrics(metrics)
    pdf.add_verdict(verdict)
    pdf.output(filename)
    return filename
